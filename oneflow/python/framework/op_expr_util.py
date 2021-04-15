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
import oneflow_api
from oneflow.python.framework.attr_util import convert_to_user_attr_value


def user_op_expr_call(self, *args, **kwargs):
    args = list(args)
    for i in range(len(args)):
        arg = args[i]
        if isinstance(arg, flow.Tensor):
            if not arg.is_determined:
                arg.determine()
            args[i] = arg._local_or_consistent_tensor

    attrs = oneflow_api.AttrValueMap()
    for attr_name, attr_value in kwargs.items():
        assert isinstance(attr_name, str)
        attrs[attr_name] = convert_to_user_attr_value(
            self.op_type_name, attr_name, attr_value
        )

    results = list(self.apply(args, attrs))
    for i, out in enumerate(results):
        tensor = flow.Tensor(*out.shape)
        tensor._local_or_consistent_tensor = out
        tensor._undetermined_tensor = None
        results[i] = tensor

    return results


def RegisterMethod4UserOpExpr():
    oneflow_api.one.UserOpExpr.__call__ = user_op_expr_call
