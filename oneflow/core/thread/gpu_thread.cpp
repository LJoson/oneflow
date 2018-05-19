#include "oneflow/core/thread/gpu_thread.h"
#include "oneflow/core/device/cuda_stream_handle.h"

namespace oneflow {

#ifdef WITH_CUDA

GpuThread::GpuThread(int64_t thrd_id, int64_t dev_id, size_t buf_size, int g_stream_priority) {
  set_thrd_id(thrd_id);
  mut_actor_thread() = std::thread([this, dev_id, buf_size, g_stream_priority]() {
    CudaCheck(cudaSetDevice(dev_id));
    void* buf_ptr = nullptr;
    if (buf_size > 0) { CudaCheck(cudaMalloc(&buf_ptr, buf_size)); }
    {
      ThreadCtx ctx;
      ctx.buf_ptr = buf_ptr;
      ctx.buf_size = buf_size;
      ctx.g_cuda_stream.reset(new CudaStreamHandle(g_stream_priority));
      PollMsgChannel(ctx);
    }
    if (buf_ptr) { CudaCheck(cudaFree(buf_ptr)); }
  });
}

#endif

}  // namespace oneflow
