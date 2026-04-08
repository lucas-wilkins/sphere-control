#include <iostream>

#include "filter.h"

int main()
{
    MedianFilter3 filter = MedianFilter3(10);

    long data[] = {
        1,1,1,1,1,2,3,3,3,3,3,4,4,4,5,6,7,8,9,0,
        0,0,0,0,0,9,9,9,8,9,0,1,0,0,0,9,9,0,0,0
    };

    long n = sizeof(data) / sizeof(data[0]);

    for (int i=0; i<n; i++)
    {
        long value = data[i];
        long filtered = filter.apply(value);
        std::cout << value << " -> " << filtered << " | " ;
        for (int j=0; j<filter.length(); j++) {
            std::cout << filter.get(j);
        }
        std::cout << std::endl;
    }
}