.PHONY: preview
preview:
	(cd preview; python preview.py &)
opengl:
	(cd lib/renderer; python opengl.py >/dev/null &)

opengl-kill:
	pkill -f opengl.py
