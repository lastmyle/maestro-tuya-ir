/**
 * Python bindings for IRremoteESP8266 library
 *
 * Provides Python access to IR protocol encoding/decoding for HVAC control.
 * Based on: https://github.com/crankyoldgit/IRremoteESP8266
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <vector>
#include <string>
#include <memory>

namespace py = pybind11;

// Forward declarations for IRremoteESP8266 classes
// We'll use a simplified interface that doesn't require actual ESP8266 hardware

/**
 * Simplified IR protocol timing structure
 * Matches the data from IRremoteESP8266 but without hardware dependencies
 */
struct IRProtocol {
    std::string name;
    std::vector<std::string> manufacturers;
    uint16_t header_mark;
    uint16_t header_space;
    uint16_t bit_mark;
    uint16_t one_space;
    uint16_t zero_space;
    uint16_t tolerance;
    uint32_t frequency;
    std::string notes;

    IRProtocol(const std::string& n, const std::vector<std::string>& m,
               uint16_t hm, uint16_t hs, uint16_t bm, uint16_t os, uint16_t zs,
               uint16_t tol = 200, uint32_t freq = 38000, const std::string& note = "")
        : name(n), manufacturers(m), header_mark(hm), header_space(hs),
          bit_mark(bm), one_space(os), zero_space(zs), tolerance(tol),
          frequency(freq), notes(note) {}
};

/**
 * Protocol database from IRremoteESP8266
 */
class IRProtocolDatabase {
private:
    std::vector<IRProtocol> protocols;

    void initializeProtocols() {
        // Fujitsu protocols
        protocols.push_back(IRProtocol(
            "FUJITSU_AC", {"Fujitsu", "Fujitsu General", "OGeneral"},
            3300, 1600, 420, 1200, 400, 300, 38000,
            "Standard Fujitsu AC protocol (ARRAH2E, AR-RAx series)"
        ));
        protocols.push_back(IRProtocol(
            "FUJITSU_AC264", {"Fujitsu"},
            3300, 1600, 420, 1200, 400, 300, 38000,
            "Extended 264-bit Fujitsu protocol"
        ));

        // Daikin protocols
        protocols.push_back(IRProtocol(
            "DAIKIN", {"Daikin"},
            3650, 1623, 428, 1280, 428, 200, 38000,
            "Daikin ARC series remotes"
        ));
        protocols.push_back(IRProtocol(
            "DAIKIN2", {"Daikin"},
            3500, 1728, 460, 1270, 420, 200, 38000,
            "Daikin ARC4xx series"
        ));

        // Mitsubishi protocols
        protocols.push_back(IRProtocol(
            "MITSUBISHI_AC", {"Mitsubishi", "Mitsubishi Electric"},
            3400, 1750, 450, 1300, 420, 200, 38000,
            "Standard Mitsubishi AC (MSZ series)"
        ));
        protocols.push_back(IRProtocol(
            "MITSUBISHI_HEAVY_152", {"Mitsubishi Heavy Industries"},
            3200, 1600, 400, 1200, 400, 200, 38000,
            "Mitsubishi Heavy SRK series"
        ));

        // Gree / Cooper & Hunter
        protocols.push_back(IRProtocol(
            "GREE", {"Gree", "Cooper & Hunter", "RusClimate", "Soleus Air"},
            9000, 4500, 620, 1600, 540, 300, 38000,
            "Gree YAW1F, Cooper & Hunter"
        ));

        // LG
        protocols.push_back(IRProtocol(
            "LG", {"LG", "General Electric"},
            8000, 4000, 600, 1600, 550, 300, 38000,
            "LG AKB series remotes"
        ));

        // Samsung
        protocols.push_back(IRProtocol(
            "SAMSUNG_AC", {"Samsung"},
            690, 17844, 690, 1614, 492, 200, 38000,
            "Samsung AR series"
        ));

        // Panasonic
        protocols.push_back(IRProtocol(
            "PANASONIC_AC", {"Panasonic"},
            3500, 1750, 435, 1300, 435, 200, 38000,
            "Panasonic CS series"
        ));

        // Hitachi protocols
        protocols.push_back(IRProtocol(
            "HITACHI_AC", {"Hitachi"},
            3400, 1700, 400, 1250, 400, 200, 38000,
            "Hitachi RAK/RAS series"
        ));
        protocols.push_back(IRProtocol(
            "HITACHI_AC1", {"Hitachi"},
            3300, 1700, 400, 1200, 400, 200, 38000,
            "Alternate Hitachi protocol"
        ));

        // Toshiba
        protocols.push_back(IRProtocol(
            "TOSHIBA_AC", {"Toshiba", "Carrier"},
            4400, 4300, 543, 1623, 543, 300, 38000,
            "Toshiba RAS series"
        ));

        // Sharp
        protocols.push_back(IRProtocol(
            "SHARP_AC", {"Sharp"},
            3800, 1900, 470, 1400, 470, 200, 38000,
            "Sharp CRMC-A series"
        ));

        // Haier
        protocols.push_back(IRProtocol(
            "HAIER_AC", {"Haier", "Daichi"},
            3000, 3000, 520, 1650, 650, 250, 38000,
            "Haier HSU series"
        ));

        // Midea / Electrolux
        protocols.push_back(IRProtocol(
            "MIDEA", {"Midea", "Comfee", "Electrolux", "Keystone", "Trotec"},
            4420, 4420, 560, 1680, 560, 300, 38000,
            "Midea MWMA series, Electrolux variants"
        ));

        // Coolix
        protocols.push_back(IRProtocol(
            "COOLIX", {"Midea", "Tokio", "Airwell", "Beko", "Bosch"},
            4480, 4480, 560, 1680, 560, 300, 38000,
            "Coolix/Midea variant used by multiple brands"
        ));

        // Carrier
        protocols.push_back(IRProtocol(
            "CARRIER_AC", {"Carrier"},
            8960, 4480, 560, 1680, 560, 300, 38000,
            "Carrier 619EGX series"
        ));

        // Electra / AEG
        protocols.push_back(IRProtocol(
            "ELECTRA_AC", {"Electra", "AEG", "AUX", "Frigidaire"},
            9000, 4500, 630, 1650, 530, 300, 38000,
            "Electra YKR series remotes"
        ));

        // Whirlpool
        protocols.push_back(IRProtocol(
            "WHIRLPOOL_AC", {"Whirlpool"},
            8950, 4484, 597, 1649, 547, 300, 38000,
            "Whirlpool SPIS series"
        ));
    }

public:
    IRProtocolDatabase() {
        initializeProtocols();
    }

    const std::vector<IRProtocol>& getProtocols() const {
        return protocols;
    }

    std::vector<std::string> getAllManufacturers() const {
        std::vector<std::string> manufacturers;
        for (const auto& proto : protocols) {
            for (const auto& mfr : proto.manufacturers) {
                if (std::find(manufacturers.begin(), manufacturers.end(), mfr) == manufacturers.end()) {
                    manufacturers.push_back(mfr);
                }
            }
        }
        std::sort(manufacturers.begin(), manufacturers.end());
        return manufacturers;
    }

    std::vector<std::string> getProtocolsByManufacturer(const std::string& manufacturer) const {
        std::vector<std::string> result;
        std::string mfr_lower = manufacturer;
        std::transform(mfr_lower.begin(), mfr_lower.end(), mfr_lower.begin(), ::tolower);

        for (const auto& proto : protocols) {
            for (const auto& mfr : proto.manufacturers) {
                std::string mfr_check = mfr;
                std::transform(mfr_check.begin(), mfr_check.end(), mfr_check.begin(), ::tolower);
                if (mfr_check == mfr_lower) {
                    result.push_back(proto.name);
                    break;
                }
            }
        }
        return result;
    }

    py::dict identifyProtocol(const std::vector<uint16_t>& timings, float tolerance_multiplier = 1.5) const {
        if (timings.size() < 4) {
            return py::dict();
        }

        uint16_t header_mark = timings[0];
        uint16_t header_space = timings[1];

        const IRProtocol* best_match = nullptr;
        double best_score = 0.0;

        for (const auto& proto : protocols) {
            uint16_t tolerance = static_cast<uint16_t>(proto.tolerance * tolerance_multiplier);

            int mark_diff = std::abs(static_cast<int>(header_mark) - static_cast<int>(proto.header_mark));
            int space_diff = std::abs(static_cast<int>(header_space) - static_cast<int>(proto.header_space));

            if (mark_diff <= tolerance && space_diff <= tolerance) {
                double mark_score = 1.0 - (static_cast<double>(mark_diff) / tolerance);
                double space_score = 1.0 - (static_cast<double>(space_diff) / tolerance);
                double total_score = (mark_score + space_score) / 2.0;

                if (total_score > best_score) {
                    best_score = total_score;
                    best_match = &proto;
                }
            }
        }

        if (best_match == nullptr) {
            return py::dict();
        }

        py::dict result;
        result["protocol"] = best_match->name;
        result["manufacturer"] = best_match->manufacturers;
        result["confidence"] = std::round(best_score * 100.0) / 100.0;

        py::dict timing_match;
        timing_match["header_mark"] = header_mark;
        timing_match["header_space"] = header_space;
        timing_match["expected_mark"] = best_match->header_mark;
        timing_match["expected_space"] = best_match->header_space;
        result["timing_match"] = timing_match;

        result["notes"] = best_match->notes;

        return result;
    }
};

/**
 * HVAC State Management
 * Simplified state structure matching stdAc::state_t from IRremoteESP8266
 */
class HVACState {
public:
    std::string protocol;
    std::string model;
    bool power;
    std::string mode;  // cool, heat, dry, fan, auto
    float degrees;     // Temperature in Celsius
    bool celsius;
    std::string fanspeed;  // auto, low, medium, high
    std::string swingv;    // vertical swing
    std::string swingh;    // horizontal swing
    bool quiet;
    bool turbo;
    bool econo;
    bool light;
    bool filter;
    bool clean;
    bool beep;
    int16_t sleep;

    HVACState()
        : protocol("UNKNOWN"), model(""), power(false), mode("auto"),
          degrees(22.0), celsius(true), fanspeed("auto"),
          swingv("off"), swingh("off"), quiet(false), turbo(false),
          econo(false), light(true), filter(false), clean(false),
          beep(true), sleep(-1) {}

    py::dict toDict() const {
        py::dict result;
        result["protocol"] = protocol;
        result["model"] = model;
        result["power"] = power;
        result["mode"] = mode;
        result["degrees"] = degrees;
        result["celsius"] = celsius;
        result["fanspeed"] = fanspeed;
        result["swingv"] = swingv;
        result["swingh"] = swingh;
        result["quiet"] = quiet;
        result["turbo"] = turbo;
        result["econo"] = econo;
        result["light"] = light;
        result["filter"] = filter;
        result["clean"] = clean;
        result["beep"] = beep;
        result["sleep"] = sleep;
        return result;
    }
};

PYBIND11_MODULE(_irremote, m) {
    m.doc() = "Python bindings for IRremoteESP8266 protocol database";

    // IRProtocol class
    py::class_<IRProtocol>(m, "IRProtocol")
        .def(py::init<const std::string&, const std::vector<std::string>&,
                     uint16_t, uint16_t, uint16_t, uint16_t, uint16_t,
                     uint16_t, uint32_t, const std::string&>(),
             py::arg("name"), py::arg("manufacturers"),
             py::arg("header_mark"), py::arg("header_space"),
             py::arg("bit_mark"), py::arg("one_space"), py::arg("zero_space"),
             py::arg("tolerance") = 200, py::arg("frequency") = 38000,
             py::arg("notes") = "")
        .def_readonly("name", &IRProtocol::name)
        .def_readonly("manufacturers", &IRProtocol::manufacturers)
        .def_readonly("header_mark", &IRProtocol::header_mark)
        .def_readonly("header_space", &IRProtocol::header_space)
        .def_readonly("bit_mark", &IRProtocol::bit_mark)
        .def_readonly("one_space", &IRProtocol::one_space)
        .def_readonly("zero_space", &IRProtocol::zero_space)
        .def_readonly("tolerance", &IRProtocol::tolerance)
        .def_readonly("frequency", &IRProtocol::frequency)
        .def_readonly("notes", &IRProtocol::notes);

    // IRProtocolDatabase class
    py::class_<IRProtocolDatabase>(m, "IRProtocolDatabase")
        .def(py::init<>())
        .def("get_protocols", &IRProtocolDatabase::getProtocols)
        .def("get_all_manufacturers", &IRProtocolDatabase::getAllManufacturers)
        .def("get_protocols_by_manufacturer", &IRProtocolDatabase::getProtocolsByManufacturer)
        .def("identify_protocol", &IRProtocolDatabase::identifyProtocol,
             py::arg("timings"), py::arg("tolerance_multiplier") = 1.5,
             "Identify IR protocol from timing array");

    // HVACState class
    py::class_<HVACState>(m, "HVACState")
        .def(py::init<>())
        .def_readwrite("protocol", &HVACState::protocol)
        .def_readwrite("model", &HVACState::model)
        .def_readwrite("power", &HVACState::power)
        .def_readwrite("mode", &HVACState::mode)
        .def_readwrite("degrees", &HVACState::degrees)
        .def_readwrite("celsius", &HVACState::celsius)
        .def_readwrite("fanspeed", &HVACState::fanspeed)
        .def_readwrite("swingv", &HVACState::swingv)
        .def_readwrite("swingh", &HVACState::swingh)
        .def_readwrite("quiet", &HVACState::quiet)
        .def_readwrite("turbo", &HVACState::turbo)
        .def_readwrite("econo", &HVACState::econo)
        .def_readwrite("light", &HVACState::light)
        .def_readwrite("filter", &HVACState::filter)
        .def_readwrite("clean", &HVACState::clean)
        .def_readwrite("beep", &HVACState::beep)
        .def_readwrite("sleep", &HVACState::sleep)
        .def("to_dict", &HVACState::toDict);
}
