# Copyright 2020 The Lucent Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Utility functions for modelzoo models."""

from __future__ import absolute_import, division, print_function

from collections import OrderedDict
from typing import List, Optional, Union


import torch.nn as nn

ACTIVATIONS = [
    nn.ELU,
    nn.Hardshrink,
    nn.Hardsigmoid,
    nn.Hardtanh,
    nn.Hardswish,
    nn.LeakyReLU,
    nn.LogSigmoid,
    nn.PReLU,
    nn.ReLU,
    nn.ReLU6,
    nn.PReLU,
    nn.SELU,
    nn.CELU,
    nn.GELU,
    nn.Sigmoid,
    nn.SiLU,
    nn.Mish,
    nn.Softplus,
    nn.Softshrink,
    nn.Softsign,
    nn.Tanh,
    nn.Tanhshrink,
    nn.Threshold,
    nn.GLU,
    nn.Softmin,
    nn.Softmax,
    nn.Softmax2d,
    nn.LogSoftmax,
    nn.AdaptiveLogSoftmaxWithLoss,
]

NORMALIZATIONS = [
    nn.BatchNorm1d,
    nn.BatchNorm2d,
    nn.BatchNorm3d,
    nn.LazyBatchNorm1d,
    nn.LazyBatchNorm2d,
    nn.LazyBatchNorm3d,
    nn.GroupNorm,
    nn.SyncBatchNorm,
    nn.InstanceNorm1d,
    nn.InstanceNorm2d,
    nn.InstanceNorm3d,
    nn.LazyInstanceNorm1d,
    nn.LazyInstanceNorm2d,
    nn.LazyInstanceNorm3d,
    nn.LayerNorm,
    nn.LocalResponseNorm,
]

POOLINGS = [
    nn.MaxPool1d,
    nn.MaxPool2d,
    nn.MaxPool3d,
    nn.MaxUnpool1d,
    nn.MaxUnpool2d,
    nn.MaxUnpool3d,
    nn.AvgPool1d,
    nn.AvgPool2d,
    nn.AvgPool3d,
    nn.FractionalMaxPool2d,
    nn.FractionalMaxPool3d,
    nn.LPPool1d,
    nn.LPPool2d,
    nn.AdaptiveMaxPool1d,
    nn.AdaptiveMaxPool2d,
    nn.AdaptiveMaxPool3d,
    nn.AdaptiveAvgPool1d,
    nn.AdaptiveAvgPool2d,
    nn.AdaptiveAvgPool3d,
]


def get_model_layers(
    model: nn.Module, 
    getLayerRepr: Optional[bool] = False,
    excludeNorms: Optional[bool] = True,
    excludeActs: Optional[bool] = True,
    excludePools: Optional[bool] = True,
) -> Union[List[str], OrderedDict[str, str]]:
    """Get the names of all layers of a network. The names are given in the format that can be used
       to access them via objectives.

    :param model: the network to get the names of
    :type model: torch.nn.Module
    :param getLayerRepr: whether to return a OrderedDict of layer names, layer representation string pair. If False just return a list of names.
    :type getLayerRepr: Optional[bool], optional
    :param excludeNorms: whether to exclude normalization layers, defaults to True
    :type excludeNorms: Optional[bool], optional
    :param excludeActs: whether to exclude Activation layers, defaults to True
    :type excludeActs: Optional[bool], optional
    :param excludePools: whether to exclude Pooling layers, defaults to True
    :type excludePools: Optional[bool], optional
    :raises ValueError: model has wrong type
    :raises ValueError: model has no modules
    :return: dict of name, repr pairs or just list of names of all layers (including activations if they are instantiated as layers)
    :rtype: Union[List[str], OrderedDict[str, str]]
    """


    # check input
    if not isinstance(model, nn.Module):
        raise ValueError(f"model should have type torch.nn.Module but has type {type(model)}")

    layers = OrderedDict() if getLayerRepr else []
    # recursive function to get names
    def recursive_get_names(net, prefix=[]):
        if hasattr(net, "_modules"):
            for name, layer in net._modules.items():
                if layer is None:
                    # e.g. GoogLeNet's aux1 and aux2 layers
                    continue
                
                # only add actual layers and not group name itself
                if (
                    not isinstance(layer, nn.Sequential)
                    and not isinstance(layer, nn.ModuleDict)
                    and not isinstance(layer, nn.ModuleList)
                    and not (any(isinstance(layer, norm) for norm in NORMALIZATIONS) and excludeNorms) # exclude normalizations
                    and not (any(isinstance(layer, acts) for acts in ACTIVATIONS) and excludeActs) # exclude activations
                    and not (any(isinstance(layer, pool) for pool in POOLINGS) and excludePools) # exclude poolings
                ):
                    if getLayerRepr:
                        layers["->".join(prefix+[name])] = layer.__repr__()
                    else:
                        layers.append("->".join(prefix + [name]))
                
                # recurse
                recursive_get_names(layer, prefix=prefix + [name])
        else:   
            raise ValueError('net has no _modules attribute! Check if your model is properly instantiated..')
    
    recursive_get_names(model)
    
    return layers