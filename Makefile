
python = ./env/bin/python
pserve = ./env/bin/pserve
conda = conda

line_length = 79
blackargs = --line-length ${line_length}
isortargs =	\
	--multi-line=3 \
	--trailing-comma \
	--force-grid-wrap=0 \
	--use-parentheses \
	--line-width=${line_length}

autoflakeargs = \
	--remove-all-unused-imports \
	--remove-unused-variables \
	--expand-star-imports

src = molecalc/*.py molecalc_lib/*.py tests/*.py

## Development

lint:
	${python} -m isort --check-only ${src} ${isortargs}
	${python} -m flake8 ${src} --count --select=E9,F63,F7,F82 --show-source --statistics
	${python} -m flake8 ${src} --count --exit-zero --max-complexity=10 --statistics
	${python} -m black --check ${blackargs} ${src}

format:
	${python} -m isort ${src} ${isortargs}
	${python} -m autoflake --in-place ${autoflakeargs} ${src}
	${python} -m black ${blackargs} ${src}

test:
	${python} -m pytest -vrs tests
	@# TODO backend tests
	@# TODO javascript tests

## Serve service

serve_development:
	ip a | grep inet
	${pserve} development.ini --reload

serve_production:
	${pyserve} production.ini

serve: serve_development

## Setup enviroment

env: conda pip setup_molecalc_in_env

conda:
	${conda} env create -f environment.yml -p env

pip:
	${python} -m pip install -r requirements.txt --ignore-installed

setup_molecalc_in_env:
	${python} -m pip install -e .

env-dev:
	${python} -m pip install -r requirements.dev.txt --ignore-installed

env-egg:
	${python} setup.py develop

dependencies:
	sudo apt install -y libxrender-dev

molecalc/data: scripts/setup_datadir.sh
	bash scripts/setup_datadir.sh

setup_assets: molecalc/static/chemdoodleweb molecalc/static/jsmol molecalc/static/fontawesome molecalc/static/jquery/jquery.min.js molecalc/static/rdkit/rdkit.js

ppqm:
	git clone https://github.com/ppqm/ppqm ppqm.git --depth 1
	ln -s ./ppqm.git/ppqm ppqm

molecalc/static/chemdoodleweb: scripts/setup_chemdoodle.sh
	bash scripts/setup_chemdoodle.sh

molecalc/static/jsmol: scripts/setup_jsmol.sh
	bash scripts/setup_jsmol.sh
	
molecalc/static/fontawesome: scripts/setup_fontawesome.sh
	bash scripts/setup_fontawesome.sh

molecalc/static/jquery/jquery.min.js: scripts/setup_jquery.sh
	bash scripts/setup_jquery.sh

molecalc/static/rdkit/rdkit.js: scripts/setup_rdkit.sh
	bash scripts/setup_rdkit.sh

## Admin

update:
	cd ppqm.git; git pull

backup:
	# Make backup of database
	cp database.sqlite database-`date +%m-%d-%Y`.sqlite

clean:
	# Remove database
	rm database.sqlite

super-clean:
	rm -r molecalc/static/jquery/jquery.min.js molecalc/static/fontawesome molecalc/static/jsmol molecalc/static/chemdoodleweb

