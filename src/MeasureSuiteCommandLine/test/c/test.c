void add_two_numbers(unsigned long *o,
                     const unsigned long *i0,
                     const unsigned long *i1) {
    // *o = *i0 + *i1;
	for (int i = 0; i < 10; i++){
		o[i] = i0[i] + i1[i];
	}
}
