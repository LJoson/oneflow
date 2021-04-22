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
import oneflow as flow
from oneflow.python.nn.module import Module
from oneflow.python.oneflow_export import oneflow_export
from oneflow.python.framework.tensor import register_tensor_op_by_module
from oneflow.python.framework.tensor import register_op_by_module
import oneflow.python.framework.id_util as id_util
from typing import Optional, Sequence
from functools import reduce
import operator


def infer_shape(x, shape):
    dim_index_need_infer = shape.index(-1) if shape.count(-1) == 1 else None
    in_elem_cnt = reduce(operator.mul, x.shape, 1)
    out_elem_cnt = reduce(operator.mul, shape, 1)
    if dim_index_need_infer is not None:
        assert (in_elem_cnt % out_elem_cnt) == 0
        shape[dim_index_need_infer] = int(abs(in_elem_cnt / out_elem_cnt))
    else:
        assert in_elem_cnt == out_elem_cnt
    return shape


@oneflow_export("Reshape")
@register_tensor_op_by_module("tmp.reshape")
@register_op_by_module("tmp.reshape")
class Reshape(Module):
    r"""
    """

    def __init__(self, shape: Sequence[int], name: Optional[str] = None,) -> None:
        super().__init__()

        assert isinstance(shape, tuple) or isinstance(shape, list)
        shape = list(shape)
        assert all(dim == -1 or dim > 0 for dim in shape)
        assert shape.count(-1) <= 1

        if name is None:
            name = id_util.UniqueStr("Reshape_")

        self._op = flow.builtin_op("reshape").Input("in").Output("out").Build()
        self.shape = shape

    def forward(self, x):
        new_shape = infer_shape(x, self.shape)
        return self._op(x, shape=new_shape)[0]
