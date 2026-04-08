#include <iostream>
#include "filter.h"
using namespace std;

Queue::Queue(long max_size)
{
    size = max_size;
    data = new long[size];
    front = 0;
    back = -1;
    count = 0;
}

Queue::~Queue()
{
    delete[] data;
}

void Queue::enqueue(long value)
{
    back = (back + 1) % size;
    data[back] = value;

    if (count == size) {
        front = (front + 1) % size;
    } else {
        count++;
    }
}

long Queue::get(int index)
{
    return data[(front + index) % size];
}

int Queue::length()
{
    return count;
}

void Queue::print() {
    for (int i = 0; i < count; i++) {
        cout << data[(front + i) % size] << " ";
    }
    cout << endl;
}

MedianFilter3::MedianFilter3(long wrap_length)
{
    queue = new Queue(3);
    wrap = wrap_length;
}

MedianFilter3::~MedianFilter3()
{
    delete queue;
}

long wrappedDistance(const long x, const long y, const long wrap)
{
    const long low = abs(x - y - wrap);
    const long base = abs(x - y);
    const long high = abs(x - y + wrap);

    return min(low, min(base, high));
}

long MedianFilter3::apply(long value)
{
    queue->enqueue(value);

    if (queue->length() == 3) {
        const long a = queue->get(0);
        const long b = queue->get(1);
        const long c = queue->get(2);

        // The following covers the cases where at least two values are the same
        if (a == b) return a;
        if (b == c) return b;
        if (c == a) return c;

        // All three values are different, we choose the central one
        // However, we need to account for wrapping
        // The middle value can be thought of as the one that is closest
        // to the other two, when wrapped

        const long ab = wrappedDistance(a, b, wrap);
        const long bc = wrappedDistance(b, c, wrap);
        const long ca = wrappedDistance(c, a, wrap);

        // In the following, we can use > without much further thought, as all values are different
        if (ab > bc) {
            if (ca > ab) {
                // ca biggest
                return b;
            } else {
                // ab biggest
                return c;
            }
        } else {
            // bc > ab
            if (ca > bc) {
                // ca biggest
                return b;
            } else {
                // bc biggest
                return a;
            }
        }

    } else {
        // Zero value case:
        //  This can't happen because it will not have been called otherwise
        // One value case:
        //  Only one value to choose, return that, i.e. `value`
        // Two value case:
        //  Both the same: There's only one value to choose, return that, i.e. `value`
        //  They're different: Choose the latest one, i.e. `value`

        return value;
    }

}

long MedianFilter3::get(int index)
{
    return queue->get(index);
}

long MedianFilter3::length()
{
    return queue->length();
}