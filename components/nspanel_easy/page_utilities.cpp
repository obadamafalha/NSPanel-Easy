// page_utilities.cpp

#ifdef NSPANEL_EASY_PAGE_UTILITIES

#include "icons.h"
#include "page_utilities.h"
#include <cstdlib> // For malloc/free
#ifdef USE_ESP_IDF
#include "esp_heap_caps.h"
#elif defined(USE_ARDUINO)
#include "esp32-hal-psram.h"
#endif

#ifndef NDEBUG_INITIAL_UTILITIES_GROUPS
    // Verify sort order in debug builds
    for (size_t i = 1; i < UTILITIES_GROUPS_COUNT; ++i) {
        assert(std::strcmp(INITIAL_UTILITIES_GROUPS[i-1].group_id, 
                          INITIAL_UTILITIES_GROUPS[i].group_id) < 0);
    }
#endif

namespace nspanel_easy {

    bool page_utilities_enabled = false;
    uint16_t page_utilities_icon_color = Colors::GRAY_LIGHT;

    UtilitiesGroupValues *UtilitiesGroups = nullptr;

    static constexpr size_t UTILITIES_GROUPS_COUNT = 8;

    void resetUtilitiesGroups() {
        cleanupUtilitiesGroups();  // Free any existing allocation first

        #ifdef USE_ESP_IDF  // To-do: Review if this arduino specific code is still needed
        UtilitiesGroups = static_cast<UtilitiesGroupValues*>(
            heap_caps_malloc(UTILITIES_GROUPS_COUNT * sizeof(UtilitiesGroupValues), MALLOC_CAP_SPIRAM));
        #elif defined(USE_ARDUINO)
        UtilitiesGroups = static_cast<UtilitiesGroupValues*>(
            ps_malloc(UTILITIES_GROUPS_COUNT * sizeof(UtilitiesGroupValues)));
        #endif  // USE_ESP_IDF
        
        if (!UtilitiesGroups) UtilitiesGroups = new UtilitiesGroupValues[UTILITIES_GROUPS_COUNT];
        if (!UtilitiesGroups) return;
    
        static constexpr UtilitiesGroupValues INITIAL_UTILITIES_GROUPS[UTILITIES_GROUPS_COUNT] = {
            {"grid", "", "", 0},      // Use "" instead of "\0" for clarity
            {"group01", "", "", 0},
            {"group02", "", "", 0},
            {"group03", "", "", 0},
            {"group04", "", "", 0},
            {"group05", "", "", 0},
            {"group06", "", "", 0},
            {"home", "", "", 0}
        };
    
        std::memcpy(UtilitiesGroups, INITIAL_UTILITIES_GROUPS, UTILITIES_GROUPS_COUNT * sizeof(UtilitiesGroupValues));
    }

    uint8_t findUtilitiesGroupIndex(const char* group_id) {
        if (UtilitiesGroups == nullptr) return UINT8_MAX;
        if (group_id == nullptr || *group_id == '\0') return UINT8_MAX;

        int low = 0;
        int high = static_cast<int>(UTILITIES_GROUPS_COUNT) - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2;
            int cmp = std::strcmp(UtilitiesGroups[mid].group_id, group_id);

            if (cmp < 0) {
                low = mid + 1;
            } else if (cmp > 0) {
                high = mid - 1;
            } else {
                return static_cast<uint8_t>(mid);  // Found
            }
        }

        return UINT8_MAX;  // Not found
    }

}  // namespace nspanel_easy

#endif  // NSPANEL_EASY_PAGE_UTILITIES
