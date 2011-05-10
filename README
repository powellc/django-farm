Django Farm
=============

A pluggable django application to keep track of animals on a farm. Simple.

Models
--------

Species
  name -> char
  slug -> from(name)
  
Breed
  species -> species
  name -> char
  slug -> from(name)
  
Animal
  name -> char
  slug -> from(name)
  breed -> breed
  mother -> animal
  father -> animal
  birthday -> date
  birthtime -> time
  description -> text
  photos -> photo[photologue]

ProductType
  name -> char (e.g. produce, meat, soap, preserves...)
  slug -> from(name)
  description -> text

Product
  name -> char
  type -> product type
  description -> text
  photos -> photo(s)[photologue]
  price -> float
  unit -> char (e.g. dozen, lb, half, whole)
  flexible_price -> char
