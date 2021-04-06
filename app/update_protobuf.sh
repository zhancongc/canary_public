cd ../protobufs || exit
/usr/local/protobuf/bin/protoc --python_out=../protocol_py/ *
cd ../app || exit
python utils/get_protocol_dict.py