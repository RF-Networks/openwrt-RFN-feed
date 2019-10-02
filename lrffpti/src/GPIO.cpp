/*
 * Copyright (c) 2016, RF Networks Ltd.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code are not permitted.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of RF Networks Ltd. nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "GPIO.h"

#include <string>
#include <sstream>
#include <fstream>
#include <iostream>
#include <exception>
#include <stdexcept>

using std::ios;
using std::endl;
using std::string;
using std::stringstream;
using std::logic_error;
using std::runtime_error;

const string GPIO::PATH_EXPORT       = "/sys/class/gpio/export";
const string GPIO::PATH_UNEXPORT     = "/sys/class/gpio/unexport";
const string GPIO::PREFIX            = "/sys/class/gpio/gpio";
const string GPIO::POSTFIX_VALUE     = "/value";
const string GPIO::POSTFIX_DIRECTION = "/direction";

GPIO::GPIO(int id) {
    id_ = id;

    Export();

    stringstream value_path;
    stringstream direction_path;

    value_path << PREFIX;
    value_path << id;
    value_path << POSTFIX_VALUE;

    direction_path << PREFIX;
    direction_path << id;
    direction_path << POSTFIX_DIRECTION;

    value_.open(value_path.str().c_str());
    direction_.open(direction_path.str().c_str());
}

GPIO::~GPIO() {
    value_.close();
    direction_.close();

    Unexport();
}

bool
GPIO::Exists() {
    stringstream path;

    path << PREFIX;
    path << id_;

    fstream gpio;

    gpio.open(path.str().c_str());

    bool result = gpio.good();

    gpio.close();

    return result;
}

void
GPIO::Export() {
    if (Exists()) return;

    fstream gpio_export;
    stringstream string_stream;

    string_stream << id_;

    gpio_export.open(PATH_EXPORT.c_str(), ios::out);
    gpio_export << string_stream.str();
    gpio_export.close();
}

void
GPIO::Unexport() {
    if (!Exists()) return;

    fstream gpio_unexport;
    stringstream string_stream;

    string_stream << id_;

    gpio_unexport.open(PATH_UNEXPORT.c_str(), ios::out);
    gpio_unexport << string_stream.str();
    gpio_unexport.close();
}

int
GPIO::Value() {
    string value;

    value_.seekp(0);
    value_ >> value;

    if (value == "0") return GPIO_LOW;
    if (value == "1") return GPIO_HIGH;

    throw logic_error("Invalid GPIO value.");
}

void
GPIO::Value(int value) {
    value_.seekp(0);

    switch (value) {
        case GPIO_LOW:
            value_ << "0" << endl;

            if (!value_.good())
                throw runtime_error("Error writting to value file stream.");

            break;
        case GPIO_HIGH:
            value_ << "1" << endl;

            if (!value_.good())
                throw runtime_error("Error writting to value file stream.");

            break;
        default:
            throw logic_error("Error cannot set invalid GPIO value.");
    }
}

int
GPIO::Direction() {
    string direction;

    direction_.seekp(0);

    direction_ >> direction;

    if (direction == "in") return GPIO_IN;
    if (direction == "out") return GPIO_OUT;

    throw logic_error("Invalid GPIO direction.");
}

void
GPIO::Direction(int value) {
    direction_.seekp(0);

    switch (value) {
        case GPIO_IN:
            direction_ << "in" << endl;

            if (!direction_.good())
                throw runtime_error("Error writting to direciton file stream.");

            break;
        case GPIO_OUT:
            direction_ << "out" << endl;

            if (!direction_.good())
                throw runtime_error("Error writting to direciton file stream.");

            break;
        default:
            throw logic_error("Error cannot set invalid GPIO direction.");
    }
}

