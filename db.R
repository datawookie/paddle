#' Title
#'
#' @return
#' @export
#'
#' @examples
connect <- function(force = FALSE) {
  # log_debug("Creating new DB connection.")

  # if (file.exists(".env")) {
  #   dotenv::load_dot_env(".env")
  # }
  #
  # DBUSER = Sys.getenv("DBUSER")
  # DBPASSWD = Sys.getenv("DBPASSWD")
  # DBHOST = Sys.getenv("DBHOST")
  # DBNAME = Sys.getenv("DBNAME")
  #
  # logger::log_debug("DB host: {DBHOST}")
  # logger::log_debug("DB name: {DBNAME}")
  # logger::log_debug("DB user: {DBUSER}")

  db <- DBI::dbConnect(
    # RPostgres::Postgres(),
    # dbname = DBNAME,
    # host = DBHOST,
    # port = 5432,
    # user = DBUSER,
    # password = DBPASSWD
    RSQLite::SQLite(),
    "kanoe.db"
  )

  invisible(db)
}
