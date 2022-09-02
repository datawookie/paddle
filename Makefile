build:
	docker build -t kanoe .

run:
	docker run -it --rm --name kanoe  -p 5000:5000 -v ${PWD}:/usr/src/app kanoe
