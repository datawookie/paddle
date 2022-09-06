#!/usr/bin/env Rscript

library(readxl)
library(janitor)
library(tidyverse)
library(jsonlite)

args = commandArgs(trailingOnly=TRUE)

if (!exists("XSLX")) XLSX <- args[1]
JSON <- sub("xlsx$", "json", XLSX)

entries <- excel_sheets(XLSX) %>%
  map(function(sheet) {
    read_xlsx(XLSX, sheet) %>%
      clean_names() %>%
      mutate(
        category = sheet,
        bc_number = as.integer(bc_number)
      )
  })

# Drop categories without entries.
#
entries <- entries[sapply(entries, nrow) != 0]
entries <- bind_rows(entries)

entries <- entries %>%
  select(
    number,
    category,
    division = div,
    last = surname,
    first = first_name,
    bcu = bc_number,
    bcu_expiry = expiry,
    club,
    klass = class
  )

write_json(
  entries,
  JSON,
  na = "null",
  pretty = TRUE
)
