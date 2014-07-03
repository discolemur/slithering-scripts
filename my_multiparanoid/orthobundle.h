#ifndef _ORTHOBUNDLE
#define _ORTHOBUNDLE

struct OrthoBundle {
	string organism1;
	vector<string> genes1;
	string organism2;
	vector<string> genes2;
	OrthoBundle(string one, string two) {
		organism1 = one;
		organism2 = two;
	}
	void print() {
		std::cout << organism1 << ": " << genes1.size() << std::endl;
		std::cout << organism2 << ": " << genes2.size() << std::endl;
		std::cout << "---------------------------------" << std::endl;
	}
};
#endif
