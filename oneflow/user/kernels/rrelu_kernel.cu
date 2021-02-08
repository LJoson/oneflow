/*
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
*/
#include "oneflow/core/framework/framework.h"

// #include <thrust/random.h>
// #include <thrust/device_vector.h>
// #include <thrust/transform.h>
// #include <thrust/iterator/counting_iterator.h>
// #include <iostream>

namespace oneflow {
namespace {

template<typename T>
__global__ void RReluForwardGpu(const int n, const float lower, const float upper, const T* x, T* y) {
thrust::default_random_engine rng;
thrust::random::uniform_real_distribution<float> dist(lower, upper);
rng.discard(1);
float alpha = dist(rng);
  CUDA_1D_KERNEL_LOOP(i, n) { y[i] = x[i] > 0 ? x[i] : x[i] * alpha; }
}

template<typename T>
__global__ void RReluBackwardGpu(const int n, const T* x, T* y, const T* dy,
                                     T* dx) {
  CUDA_1D_KERNEL_LOOP(i, n) { dx[i] = x[i] > 0 ? dy[i] : dy[i] * y / x; }
}

}  // namespace

template<typename T>
class GpuRReluKernel final : public user_op::OpKernel {
 public:
  GpuRReluKernel() = default;
  ~GpuRReluKernel() = default;

 private:
  void Compute(user_op::KernelComputeContext* ctx) const override {
    const user_op::Tensor* x = ctx->Tensor4ArgNameAndIndex("x", 0);
    user_op::Tensor* y = ctx->Tensor4ArgNameAndIndex("y", 0);
    const int32_t elem_cnt = x->shape().elem_cnt();
    const float lower = ctx->Attr<float>("lower");
    const float upper = ctx->Attr<float>("upper");

    RUN_CUDA_KERNEL((RReluForwardGpu<T>), ctx->device_ctx(), elem_cnt, lower, upper,
                    x->dptr<T>(), y->mut_dptr<T>());
  }
  bool AlwaysComputeWhenAllOutputsEmpty() const override { return false; }
};

#define REGISTER_GPU_RRELU_KERNEL(dtype)             \
  REGISTER_USER_KERNEL("rrelu")                      \
      .SetCreateFn<GpuRReluKernel<dtype>>()           \
      .SetIsMatchedHob((user_op::HobDeviceTag() == "gpu") \
                       & (user_op::HobDataType("y", 0) == GetDataType<dtype>::value));

REGISTER_GPU_RRELU_KERNEL(float)
REGISTER_GPU_RRELU_KERNEL(double)

template<typename T>
class GpuRReluGradKernel final : public user_op::OpKernel {
 public:
  GpuRReluGradKernel() = default;
  ~GpuRReluGradKernel() = default;

 private:
  void Compute(user_op::KernelComputeContext* ctx) const override {
    const user_op::Tensor* x = ctx->Tensor4ArgNameAndIndex("x", 0);
    const user_op::Tensor* y = ctx->Tensor4ArgNameAndIndex("y", 0);
    const user_op::Tensor* dy = ctx->Tensor4ArgNameAndIndex("dy", 0);
    user_op::Tensor* dx = ctx->Tensor4ArgNameAndIndex("dx", 0);
    const int32_t elem_cnt = x->shape().elem_cnt();

    RUN_CUDA_KERNEL((RReluBackwardGpu<T>), ctx->device_ctx(), elem_cnt,
                    x->dptr<T>(), y->dptr<T>(), dy->dptr<T>(), dx->mut_dptr<T>());
  }
  bool AlwaysComputeWhenAllOutputsEmpty() const override { return false; }
};

#define REGISTER_GPU_RRELU_GRAD_KERNEL(dtype)        \
  REGISTER_USER_KERNEL("rrelu_grad")                 \
      .SetCreateFn<GpuRReluGradKernel<dtype>>()       \
      .SetIsMatchedHob((user_op::HobDeviceTag() == "gpu") \
                       & (user_op::HobDataType("dx", 0) == GetDataType<dtype>::value));

REGISTER_GPU_RRELU_GRAD_KERNEL(float)
REGISTER_GPU_RRELU_GRAD_KERNEL(double)

}  // namespace oneflow