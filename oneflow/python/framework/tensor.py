"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import oneflow_api
from oneflow.python.oneflow_export import oneflow_export
import oneflow.python.framework.device as oneflow_device

oneflow_export("LocalTensor")(oneflow_api.LocalTensor)

oneflow_export("ConsistentTensor")(oneflow_api.ConsistentTensor)


@oneflow_export("tensor")
class Tensor:
    def __init__(
        self,
        shape,
        dtype,
        device=None,
        requires_grad=True,
        retain_grad=False,
        is_leaf=True,
        placement=None,
    ):
        self.shape = shape
        self.dtype = dtype
        self.device = device
        self.requires_grad = requires_grad
        self.retain_grad = retain_grad
        self.is_leaf = is_leaf
        self.placement = placement
        self.local_tensor = None
        self.consistent_tensor = None

    @property
    def shape(self):
        return self.shape

    @property
    def device(self):
        pass

    @property
    def ndim(self):
        pass

    @property
    def is_cuda(self):
        pass

    @property
    def dtype(self):
        pass

    @property
    def data(self):
        pass

    @property
    def grad(self):
        pass

    @property
    def grad_fn(self):
        pass

    @property
    def requires_grad(self):
        pass

    @property
    def is_leaf(self):
        pass

    @property
    def placement(self):
        pass

    @property
    def is_lazy(self):
        pass

    @property
    def is_consistent(self):
        pass

    def size(self):
        pass

    def dim(self):
        pass

    def ndimension(self):
        pass

    def get_device(self):
        pass

    def nelemenet(self):
        pass

    def data_ptr(self):
        pass

    def element_size(self):
        pass

    def numpy(self):
        pass

    def tolist(self):
        pass

    def backward(self):
        pass

    def set_device(self, device):
        pass

    def set_placement(self, placement):
        pass

    def set_distribute(self, distribute):
        pass

    def set_dtyp(self, dtype):
        pass

    def set_consistent(self, is_consistent):
        pass

    def determined(self):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __array__(self):
        pass

    def __sizeof__(self):
        pass
