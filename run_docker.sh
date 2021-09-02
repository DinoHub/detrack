WORKSPACE=/media/data/detrack
# DATA=/media/data/deep_sort_realtime
# DATA2=/media/data/ScaledYOLOv4

docker run -it \
	--gpus all \
    -w $WORKSPACE \
	-v $WORKSPACE:$WORKSPACE \
	detrack
