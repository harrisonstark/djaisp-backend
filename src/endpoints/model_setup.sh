
#these instructions should hopefully work and allow you to implement the model
#although they don't on my Mac
sudo apt install bazel
git clone https://www.github.com/tensorflow/models #it really only needs the layers, models, tf_ops, and tflite_ops within models/research/seq_flow_lite
models/research/seq_flow_lite/demo/colab/setup_workspace.sh
pip install models/research/seq_flow_lite
rm -rf models/research/seq_flow_lite/tf_ops #think this can be commented out
rm -rf models/research/seq_flow_lite/tflite_ops #this too
mv models models_folder
#moving the relevant files up to this directory, can make that cleaner later
mv models_folder/research/seq_flow_lite/models models
mv models_folder/research/seq_flow_lite/layers layers
mv models_folder/research/seq_flow_lite/tf_ops tf_ops
mv models_folder/research/seq_flow_lite/tflite_ops tflite_ops
#since we're not training the model, just loading it back up, these should be all it needs