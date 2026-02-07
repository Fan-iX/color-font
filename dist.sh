git show bio:tint-fasta.py | python3 - CascadiaMono.ascii.ttf dist/CascadiaMonoProt.ttf --palette-map <(git show bio:prot.map)
git show bio:tint-fasta.py | python3 - CascadiaMono.ascii.ttf dist/CascadiaMonoNucl.ttf --palette-map <(git show bio:nucl.map)
git show main:tint.py | python3 - CascadiaMono.ascii.ttf dist/CascadiaMonoChemJmol.ttf --palette-map <(git show chem:jmol.map)
git show main:tint.py | python3 - CascadiaMono.ascii.ttf dist/CascadiaMonoChemJmolLight.ttf --palette-map <(git show main:remap-palette.py | python3 - <(git show chem:jmol.map) --l-to 0.3 0.7)
git show main:scriptify.py | python3 - CascadiaMono.ascii.ttf dist/CascadiaMonoScript.ttf
git show chem:scriptify-chem.py | python3 - LiberationSerif.ascii.ttf dist/LiberationSerifScriptChem.ttf
