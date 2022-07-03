library(rvest)
library(dplyr)
library(purrr)
library(janitor)

URL_BASE <- "https://canoeracing.org.uk/marathon/results"

html <- read_html(file.path(URL_BASE, "results2021.html"))

clubs <- html %>%
  html_nodes("td > a") %>%
  html_attr("href") %>%
  # .[1:2] %>%
  map(function(href) {
    url <- file.path(URL_BASE, href)
    print(url)
    html <- read_html(url)

    tables <- html %>%
      html_nodes("table[border='1']")

    tables %>%
      map(function(table) {
        table %>%
          html_table() %>%
          clean_names() %>%
          pull(club)
      }) %>%
      unlist()
  }) %>%
  unlist()

clubs <- clubs %>%
  map(~ substring(., c(1, 4), c(3, 6))) %>%
  unlist() %>%
  unique()

clubs <- clubs[clubs != ""]

clubs <- data.frame(code = clubs) %>%
  arrange(code)

write.csv(clubs, file = "database/club-list.csv", row.names = FALSE, quote = FALSE)
