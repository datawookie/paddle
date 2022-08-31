library(readr)
library(tidyverse)
library(janitor)
library(DBI)

source("db.R")

data <- read_delim("time-trial-results-2.5.csv", delim = ";")

data <- data %>%
  select(-TTs, -PB) %>%
  clean_names() %>%
  rename(name = x2_5_mile) %>%
  mutate(across(starts_with("x"), as.character)) %>%
  pivot_longer(-name, names_to = "date", values_to = "time") %>%
  filter(!is.na(time)) %>%
  mutate(
    date = str_replace(date, "^x", ""),
    date = str_replace_all(date, "_", "/"),
    date = as.Date(date, format = "%d/%m/%Y"),
    name = str_squish(name)
  )

data <- data %>%
  nest(data = -name) %>%
  mutate(
    member_id = row_number()
  ) %>%
  arrange(name)

db <- connect()

dbAppendTable(
  db,
  "member",
  data %>%
    select(id = member_id, first = name)
)

data <- data %>%
  unnest(data) %>%
  nest(data = -date) %>%
  arrange(date) %>%
  mutate(
    distance = 2.5,
    time_trial_id = row_number(),
    date = format(date)
  )

dbAppendTable(
  db,
  "time_trial",
  data %>% select(id = time_trial_id, date, distance)
)

data <- data %>%
  unnest(data)

dbAppendTable(
  db,
  "time_trial_result",
  data %>% select(time_trial_id, member_id, time)
)

