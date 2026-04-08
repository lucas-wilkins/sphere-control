//
// Created by lucas on 06/04/2026.
//

#ifndef MEDIAN_FILTER_FILTER_H
#define MEDIAN_FILTER_FILTER_H


class Queue {
    int size;
    long* data;
    int front;
    int back;
    int count;

public:
    Queue(long max_size);
    ~Queue();

    int length();
    void enqueue(long value);
    long get(int index);
    void print();
};

class MedianFilter3 {
    Queue* queue;
    int wrap;

public:
    MedianFilter3(long wrap_length);
    ~MedianFilter3();

    long apply(long value);
    long get(int index);
    long length();

};

#endif //MEDIAN_FILTER_FILTER_H