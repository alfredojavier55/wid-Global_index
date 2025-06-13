library(ggplot2)
library(dplyr)
library(tidyr)
library(stringr)

getwd()
setwd("/home/aa/fli/wid-Global_index/")
m <- read.csv(file = "classified_papers_metric_clean.csv", sep =  ",", header = TRUE)
head(m)
colnames(m)
table(m$classification)
table(m$human)
table(m$country)

#Checking countries to plot
m <- m %>% filter(human == 1)

m$country <- str_to_title(m$country)  # Capitalize country names
m$country <- str_replace_all(m$country, "Usa", "USA")  # Replace "United States" with "USA"
m$country <- str_replace_all(m$country, "Uk", "UK")  # Replace "United States" with "USA"

View(m)
# Get world map data
world_map <- map_data("world")

# Join your data to the map data
map_data_joined <- left_join(world_map, m, by = c("region" = "country"))

m_count <- m %>%
  group_by(country, Disease) %>%
  summarise(n = n(), .groups = "drop")

map_data_joined <- left_join(world_map, m_count, by = c("region" = "country"))


colnames(map_data_joined)

table(world_map$region)
table(map_data_joined$disease)

View(map_data_joined)

# Plot
sm <- ggplot(map_data_joined, aes(long, lat, group = group, fill = Disease)) +
  geom_polygon(color = "gray80", size = 0.3) +
  labs(title = "Optimization papers included by Disease (12)",
       fill = "Disease") +
  scale_fill_discrete(na.value = "white") +
  theme_void() +
  ylim(c(0, 90))  # Adjust y limits to focus on the world map

sm
ggsave("world_map_disease.png", plot = sm, width = 10, height = 6)
