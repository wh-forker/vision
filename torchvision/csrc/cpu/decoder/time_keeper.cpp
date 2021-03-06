// Copyright 2004-present Facebook. All Rights Reserved.

#include "time_keeper.h"

extern "C" {
#include <libavutil/avutil.h>
}

namespace ffmpeg {

namespace {
const ssize_t kMaxTimeBaseDiference = 10;
}

ssize_t TimeKeeper::adjust(ssize_t& decoderTimestamp) {
  const ssize_t now = std::chrono::duration_cast<std::chrono::microseconds>(
                          std::chrono::system_clock::now().time_since_epoch())
                          .count();

  if (startTime_ == 0) {
    startTime_ = now;
  }
  if (streamTimestamp_ == 0) {
    streamTimestamp_ = decoderTimestamp;
  }

  const auto runOut = startTime_ + decoderTimestamp - streamTimestamp_;

  if (std::labs((now - runOut) / AV_TIME_BASE) > kMaxTimeBaseDiference) {
    streamTimestamp_ = startTime_ - now + decoderTimestamp;
  }

  const auto sleepAdvised = runOut - now;

  decoderTimestamp += startTime_ - streamTimestamp_;

  return sleepAdvised > 0 ? sleepAdvised : 0;
}

} // namespace ffmpeg
