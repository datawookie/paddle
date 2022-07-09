library(readxl)
library(janitor)
library(dplyr)
library(jsonlite)

XLSX <- "entries-2022-race-A.xlsx"
JSON <- sub("xlsx$", "json", XLSX)

doubles <- read_xlsx(XLSX, "Doubles", col_names = TRUE)
singles <- read_xlsx(XLSX, "Singles", col_names = FALSE)

doubles <- doubles %>% clean_names()
names(singles) <- names(doubles)

fix_columns <- function(df) {
  df %>%
    select(number:div) %>%
    select(-expiry) %>%
    rename(
      last = surname,
      first = first_name,
      bcu = bc_number,
      class = class_7,
      division = div
    )
}
doubles <- fix_columns(doubles)
singles <- fix_columns(singles)

entries <- rbind(singles, doubles)

write_json(entries, JSON, pretty = TRUE)
