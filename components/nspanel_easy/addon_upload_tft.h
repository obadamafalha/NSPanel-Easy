// addon_upload_tft.h - Complete TFT component state management

#pragma once

#ifdef NSPANEL_EASY_ADDON_UPLOAD_TFT

#include <cstdint>

namespace nspanel_easy {

    // TFT upload state variables (previously YAML globals)
    extern uint8_t tft_upload_attempt;
    extern bool tft_upload_result;

}  // namespace nspanel_easy

#endif  // NSPANEL_EASY_ADDON_UPLOAD_TFT
