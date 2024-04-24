build:
	docker build -t paddle .

run: build
	docker run -it --rm --name paddle  -p 5000:5000 -v ${PWD}:/usr/src/app paddle
