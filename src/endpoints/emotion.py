import tensorflow as tf
from layers import base_layers
from layers import projection_layers
from models import prado


LABELS = [
    'admiration',
    'amusement',
    'anger',
    'annoyance',
    'approval',
    'caring',
    'confusion',
    'curiosity',
    'desire',
    'disappointment',
    'disapproval',
    'disgust',
    'embarrassment',
    'excitement',
    'fear',
    'gratitude',
    'grief',
    'joy',
    'love',
    'nervousness',
    'optimism',
    'pride',
    'realization',
    'relief',
    'remorse',
    'sadness',
    'surprise',
    'neutral',
]

MODEL_CONFIG = {
    'labels': LABELS,
    'multilabel': True,
    'quantize': False,
    'max_seq_len': 128,
    'max_seq_len_inference': 128,
    'exclude_nonalphaspace_unicodes': False,
    'split_on_space': True,
    'embedding_regularizer_scale': 0.035,
    'embedding_size': 128,
    'bigram_channels': 64,
    'trigram_channels': 64,
    'feature_size': 512,
    'network_regularizer_scale': 0.0001,
    'keep_prob': 0.5,
    'word_novelty_bits': 0,
    'doc_size_levels': 0,
    'add_bos_tag': False,
    'add_eos_tag': False,
    'pre_logits_fc_layers': [],
    'text_distortion_probability': 0.0,
}

VALENCE_MAP = {
    'admiration': 0.6,
    'amusement': 0.5,
    'anger': 0.1,
    'annoyance': 0.3,
    'approval': 0.6,
    'caring': 0.6,
    'confusion': 0.4,
    'curiosity': 0.4,
    'desire': 0.4,
    'disappointment': 0.3,
    'disapproval': 0.2,
    'disgust': 0.2,
    'embarrassment': 0.4,
    'excitement': 0.7,
    'fear': 0.1,
    'gratitude': 0.6,
    'grief': 0.1,
    'joy': 0.9,
    'love': 0.9,
    'nervousness': 0.4,
    'optimism': 0.5,
    'pride': 0.7,
    'realization': 0.4,
    'relief': 0.7,
    'remorse': 0.3,
    'sadness': 0.2,
    'surprise': 0.5,
    'neutral': 0.5,
}

AROUSAL_MAP = {
    'admiration': 0.4,
    'amusement': 0.2,
    'anger': 0.9,
    'annoyance': 0.6,
    'approval': 0.3,
    'caring': 0.3,
    'confusion': 0.5,
    'curiosity': 0.2,
    'desire': 0.5,
    'disappointment': 0.2,
    'disapproval': 0.3,
    'disgust': 0.5,
    'embarrassment': 0.5,
    'excitement': 0.7,
    'fear': 0.9,
    'gratitude': 0.7,
    'grief': 0.9,
    'joy': 0.9,
    'love': 0.5,
    'nervousness': 0.4,
    'optimism': 0.2,
    'pride': 0.4,
    'realization': 0.7,
    'relief': 0.2,
    'remorse': 0.2,
    'sadness': 0.7,
    'surprise': 1.0,
    'neutral': 0.5,
}


def build_model(mode):
  # define our inputs.
  inputs = []
  input = tf.keras.Input(shape=(), name='input', dtype='string')
  projection_layer = projection_layers.ProjectionLayer(MODEL_CONFIG, mode) #projection layer import isnt working because of???
  projection, sequence_length = projection_layer(input)
  inputs = [input]
  # model layer.
  model_layer = prado.Encoder(MODEL_CONFIG, mode)
  logits = model_layer(projection, sequence_length)
  #activate
  activation = tf.keras.layers.Activation('sigmoid', name='predictions')
  predictions = activation(logits)
  #return keras model
  model = tf.keras.Model(
      inputs=inputs,
      outputs=[predictions])

  return model

