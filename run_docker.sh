WORKSPACE=/media/data/od_tracking

docker run -it \
	--gpus all \
	--net host \
    -w $WORKSPACE \
	-v $WORKSPACE:$WORKSPACE \
	-v $HOME/.Xauthority:/root/.Xauthority:rw \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-e DISPLAY=unix$DISPLAY \
	-e QT_X11_NO_MITSHM=1 \
	od_tracking
