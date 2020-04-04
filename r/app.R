# Load libraries ----------------------------------------------------------

base::library(package = config)
base::library(package = DBI)
base::library(package = RMySQL)
base::library(package = shiny)
base::library(package = tidyverse)

# Extract data ------------------------------------------------------------

# Kill existing connections
for (i in RMySQL::dbListConnections(drv = RMySQL::MySQL())) {
  RMySQL::dbDisconnect(conn = i)
}

# Set new connections
qs <- config::get(value = 'quantified_self')
qs_con <- DBI::dbConnect(drv = RMySQL::MySQL(),
                         user = qs$user,
                         password = qs$password, 
                         dbname = qs$dbname)

# Extract
summary_df <- DBI::dbGetQuery(conn = qs_con, 
                              statement = 'SELECT * FROM summary')

# Define helper functions -------------------------------------------------

# Map from activity name to key name
map_value_to_key <- function(act_name) {
  dplyr::case_when(
    act_name == '1 - Reflecting' ~ 'reflecting',
    act_name == '2 - Spending time with Laura' ~ 'laura',
    act_name == '3 - Spending time with family' ~ 'family',
    act_name == '4 - Spending time with friends' ~ 'friends',
    act_name == '5 - Sleeping' ~ 'sleeping',
    act_name == '6 - Learning' ~ 'learning',
    act_name == '7 - Working' ~ 'working',
    act_name == '8 - Working out' ~ 'working_out',
    act_name == '9 - Serving' ~ 'serving',
    act_name == '10 - Waste' ~ 'waste'
  )
}

# Calculate effectiveness values corresponding to given activity values
calc_eff_values <- function(act_name, act_values) {
  temp_chr <- map_value_to_key(act_name = act_name)
  temp_l  <- config::get(value = temp_chr,
                         file = 'params.yml')
  num <- temp_l$max_eff * 2
  temp_num <- base::as.numeric(x = temp_l$steep)
  denom <- 1 + base::exp(x = -1 * temp_num * (act_values - temp_l$act_mid))
  num / denom - temp_l$max_eff
}

# Calculate range of values between activity min and max (for plotting)
calc_act_range <- function(act_name) {
  temp_chr <- map_value_to_key(act_name = act_name)
  temp_l  <- config::get(value = temp_chr,
                         file = 'params.yml')
  base::seq(from = temp_l$min_act,
            to = temp_l$max_act,
            by = .01)
}

# Transform data ----------------------------------------------------------

# Convert type
summary_df$start_datetime <- lubridate::ymd_hms(
  summary_df$start_datetime
  )

# Calculate effectiveness values
summary_df <- summary_df %>%
  dplyr::mutate(effectiveness_value = purrr::map2_dbl(
    .x = activity_name, 
    .y = activity_value, 
    .f = calc_eff_values
    ))

# Create background frame


# Define UI ---------------------------------------------------------------

ui <- shiny::fluidPage(
  # Title
  shiny::titlePanel(title = 'I-count-ability'),
  
  # Date range
  shiny::fluidRow(shiny::dateRangeInput(
    inputId = 'dates', 
    label = 'Select date range:', 
    start = base::as.character(x = base::min(summary_df$start_datetime)),
    end = base::as.character(x = base::max(summary_df$start_datetime)),
    min = base::as.character(x = base::min(summary_df$start_datetime)),
    max = base::as.character(x = base::max(summary_df$start_datetime))
  )),
  
  # Summary plot
  shiny::plotOutput(outputId = 'summary'),
  
  # Detail plots
  shiny::fluidRow(
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail1')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail2')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail3')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail4')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail5')),
  ),
  shiny::fluidRow(
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail6')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail7')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail8')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail9')),
    shiny::column(width = 2, 
                  shiny::plotOutput(outputId = 'detail10')),
  ) 
)

# Define server -----------------------------------------------------------

server <- function(input, output, session) {
  # Date range
  shiny::observe(x = {
    shiny::updateDateRangeInput(session = session, 
                                inputId = 'dates')
  })
  
  # Summary data
  data <- shiny::reactive(x = {
    summary_df %>%
      dplyr::filter(start_datetime >= lubridate::ymd(input$dates[1]),
                    start_datetime <= lubridate::ymd(input$dates[2])) %>%
      dplyr::group_by(start_datetime) %>%
      dplyr::summarise(effectiveness_value = sum(effectiveness_value))
  })

  # Summary plot
  output$summary <- shiny::renderPlot(expr = {
    ggplot2::ggplot(data = data(),
                    mapping = ggplot2::aes(x = start_datetime,
                                           y = effectiveness_value)) +
      ggplot2::geom_bar(stat = 'identity')
    })
  
  # Detail data
  data2 <- shiny::reactive(x = {
    summary_df %>%
      dplyr::filter(start_datetime == lubridate::ymd(input$dates[2]))
  })
  
  # Detail 1 plot
  output$detail1 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '1 - Reflecting') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '1 - Reflecting'),
          effectiveness_value = calc_eff_values(
            act_name = '1 - Reflecting', 
            act_values = activity_value
            ))) +
      ggplot2::ylim(-105, 105)
    })

  # Detail 2 plot
  output$detail2 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '2 - Spending time with Laura') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '2 - Spending time with Laura'),
          effectiveness_value = calc_eff_values(
            act_name = '2 - Spending time with Laura', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 3 plot
  output$detail3 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '3 - Spending time with family') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '3 - Spending time with family'),
          effectiveness_value = calc_eff_values(
            act_name = '3 - Spending time with family', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 4 plot
  output$detail4 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '4 - Spending time with friends') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '4 - Spending time with friends'),
          effectiveness_value = calc_eff_values(
            act_name = '4 - Spending time with friends', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 5 plot
  output$detail5 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '5 - Sleeping') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '5 - Sleeping'),
          effectiveness_value = calc_eff_values(
            act_name = '5 - Sleeping', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 6 plot
  output$detail6 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '6 - Learning') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '6 - Learning'),
          effectiveness_value = calc_eff_values(
            act_name = '6 - Learning', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 7 plot
  output$detail7 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '7 - Working') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '7 - Working'),
          effectiveness_value = calc_eff_values(
            act_name = '7 - Working', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 8 plot
  output$detail8 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '8 - Working out') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '8 - Working out'),
          effectiveness_value = calc_eff_values(
            act_name = '8 - Working out', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 9 plot
  output$detail9 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '9 - Serving') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '9 - Serving'),
          effectiveness_value = calc_eff_values(
            act_name = '9 - Serving', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
  
  # Detail 10 plot
  output$detail10 <- shiny::renderPlot(expr = {
    data2() %>%
      dplyr::filter(activity_name == '10 - Waste') %>%
      ggplot2::ggplot(mapping = ggplot2::aes(x = activity_value, 
                                             y = effectiveness_value)) +
      ggplot2::geom_point() +
      ggplot2::geom_line(
        data = dplyr::tibble(
          activity_value = calc_act_range(act_name = '10 - Waste'),
          effectiveness_value = calc_eff_values(
            act_name = '10 - Waste', 
            act_values = activity_value
          ))) +
      ggplot2::ylim(-105, 105)
  })
}

# Create app --------------------------------------------------------------

shiny::shinyApp(ui = ui,
                server = server)