library(dplyr)
library(tidyr)

raceA <- read.csv("2024-waterside-race-a-entries.txt", header = FALSE)
raceB <- read.csv("2024-waterside-race-b-entries.txt", header = FALSE)
# Add for raceC when available
# raceC <- read.csv("2024-waterside-race-c-entries.txt", header = FALSE, stringsAsFactors = FALSE)

# Create a unique identifier for each team by concatenating the first four columns (V1-V4)

raceA <- raceA %>% mutate(unique_id = paste(V1, V2, V3, V4, sep = "_"))
raceB <- raceB %>% mutate(unique_id = paste(V1, V2, V3, V4, sep = "_"))
# Repeat for Race C when available:
# raceC <- raceC %>% mutate(unique_id = paste(V1, V2, V3, V4, sep = "_"))

# Rename the race number column for clarity
raceA <- raceA %>% rename(race_number_A = V7)
raceB <- raceB %>% rename(race_number_B = V7)
# For Race C:
# raceC <- raceC %>% rename(race_number_C = V7)

# Merging Race  data based on the unique team identifier.

merged_race <- full_join(raceA, raceB, by = "unique_id")
# To include Race C, consider using :
#merged_race <- full_join(merged_race, raceC, by = "unique_id")


# Separate the unique identifier back into individual components (V1-V4).

merged_race <- merged_race %>%
  separate(unique_id, into = c("V1", "V2", "V3", "V4"), sep = "_", remove = TRUE)

final_dataset <- merged_race %>%
  select(V1, V2, V3, V4, V5 = V5.x, V6 = V6.x, race_number_A, race_number_B, V8 = V8.x, V9 = V9.x, V10 = V10.x, V11 = V11.x, V12 = V12.x)

# Add missing columns
colnames_to_add <- setdiff(paste("V", 8:11, sep = ""), names(final_dataset))
for (col in colnames_to_add) {
  final_dataset[[col]] <- ""
}

# Define the desired column order

base_columns <- c(names(final_dataset)[!names(final_dataset) %in% c(paste("V", 8:12, sep = ""))], paste("V", 8:11, sep = ""))

# Reorder the dataset
final_dataset <- final_dataset[base_columns]

# Exclude the first row from the dataset
final_dataset_to_save <- final_dataset[-1, ]

write.table(final_dataset_to_save, "2024-waterside-merged-races.txt", row.names = FALSE, col.names = FALSE, sep = ",", na = "", quote = FALSE)
