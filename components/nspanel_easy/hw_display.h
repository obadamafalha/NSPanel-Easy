// hw_display.h

#pragma once

#ifdef NSPANEL_EASY_HW_DISPLAY

#include <cstdint>
#include <vector>
#include "esphome/core/defines.h"
#include "esphome/core/helpers.h"
#include "esphome/core/log.h"
#include "pages.h"
#include "base.h"

namespace nspanel_easy {

    extern uint8_t brightness_current;
    extern uint8_t display_mode;
    extern uint8_t display_charset;

}  // namespace nspanel_easy

#endif  // NSPANEL_EASY_HW_DISPLAY
