# Title: Attack Target Generator
# Author: Brandon Klett
# Date Created: 02/23/2024
# Date Modified: 03/29/24
# Description: 
  Attack Target Generator aims to reduce the amount of hand jamming grids from large target sets.
  This is accomplished by taking the grid, its designation of h for hostile and f for friendly, and the title
  of of the item in order from a csv. MGRS is then converted to lat long for reading by the mgrs library
  and joined together for concatination into cot data file. Follwoing the data files creation a manifiest is 
  generated and the cot files are ziped up for ingestion looking like a ATAK data package. Once introduced 
  to ATAK, it plots to the users EUD based on the provided information.
  
