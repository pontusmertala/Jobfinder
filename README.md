# Jobfinder

Dataset Ändringar

Rensade datasetet 2023.csv genom att bara behålla kolumnerna headline, description, occupation

Ersatte den nuvarande kolumnen "occupation"  med en ny kolumn med samma namn där vi la endast jobbtiteln, som vi fick fram genom att ta det som kom efter "label:" i den gamla kolumnen.

La till ett dataset med SSYK koder från https://www.scb.se/dokumentation/klassifikationer-och-standarder/standard-for-svensk-yrkesklassificering-ssyk/, där vi matchade våra jobbtitlar med titlar i excelfilen och tilldelade de matchande titlarna tillhörande ssyk kod för att kunna få en generell jobb beskrivning för varje yrke.

Använde oss av fuzzywuzzy bibloteket i python för att matcha de titlarna som ej stämde överens 100% med excel filen och utefter en så hög procentuell matchning med liknande arbetstitlar tilldelade den ssyk kod med högst "matchning" ett exempel på detta va att vi hade titeln programmerare/systemutvecklare i vårat dataset men i excel filen va denna jobbtitel 2 olika jobbtitlar.
