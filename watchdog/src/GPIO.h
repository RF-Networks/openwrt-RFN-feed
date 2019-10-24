/*
 * GPIO.h
 *
 *  Created on: May 3, 2016
 *      Author: rf-networks
 */

#ifndef GPIO_H_
#define GPIO_H_

#include <string>
#include <fstream>
#include <iostream>

using std::string;
using std::fstream;

enum GPIODirection {
	GPIO_IN = 0,
	GPIO_OUT = 1
};

enum GPIOValue {
	GPIO_LOW = 0,
	GPIO_HIGH = 1
};

class GPIO {
    public:
        explicit GPIO(int id);
        ~GPIO();

        int  Value();
        void Value(int value);
        int  Direction();
        void Direction(int value);

    private:
        int id_;

        fstream value_;
        fstream direction_;

        bool Exists();
        void Export();
        void Unexport();

        static const string PATH_EXPORT;
        static const string PATH_UNEXPORT;
        static const string PREFIX;
        static const string POSTFIX_VALUE;
        static const string POSTFIX_DIRECTION;
};

#endif /* GPIO_H_ */
