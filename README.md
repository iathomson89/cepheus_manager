# cepheus_manager
Intended to run all the various moving parts of the Cepheus RPG from the command line


NOTE: Trade codes are slightly modified in the planets database. As is now Ast, and In is now Ind, in order to avoid conflicts with SQL terminology.

# Conventions
I typically import the cepheus_manager package as cc, and may use that as shorthand throughout.

# Getting Started
Run cepheus_build.py to build the database.

## Planet Data
If you have planet data from a site such as travellermap.com, you can mass import it by copying and pasting the planet data into a .txt file {filename} in the data_sources folder.

Run mass_import_planets({filename}) to import all of those planets into the planets table at once.

If you'd like a document with a more detailed readout for a specific planet, run cc.create_pprofile(planet_name). This will generate a txt file with the planet data spelled out in a slightly more user-friendly manner. As long as you don't mess up the data format in the first line, you can make whatever edits you like to the planet profile itself for your own notes. 

If for any reason you need to rebuild the database, you can also import data back into the database from those planet profiles by running add_from_pprofile(planet_name) for a single profile, or add_all_pprofiles() to import every planet profile at once. 


# Useful Functions:
make_crew() - create a new crew, step by step.

hire_crew() - walks the user through adding a crew member (player or NPC) step by step. Easier than using the direct add_crew_member() function, which requires input for all lines. 

mass_import_planets(sec_file) - If you have a file with GENie-formatted data from a site like travellermap.com, you can paste it into a txt file and save it under "data_sources". If you then call mass_import_planets({your_filename}), it will import all of those planets at once. 

create_pprofile(planet_name) - creates a planet profile txt in the pprofiles folder. This profile starts with the GENie format string for the planet, for easy import later, as well as a plain-language breakdown of planet statistics