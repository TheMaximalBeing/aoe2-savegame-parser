import extract_ai

# all AIs will be extracted from this save file
savefile_to_extract_ais = "data/test-ai-load.gaz"

# dont add .per here
# output files are named like 'base_1.per' 'base_2.per' etc
basename_of_extracted_ais = "output/extracted_ai"

extract_ai.extract_ais_from_save(savefile_to_extract_ais, basename_of_extracted_ais)

