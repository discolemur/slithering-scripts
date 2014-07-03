#ifndef _ORTHOSTREAM
#define _ORTHOSTREAM

using std::string;
using std::ifstream;
using std::vector;
using std::endl;
using std::cout;

class OrthoStream {

private:
	string org1;
	string org2;
	vector<OrthoBundle> bundles;
	int counter;

	struct Split {
		string id;
		string org;
		string gene;
	};

	Split split_line(string& line) {
		std::stringstream ss;
		ss.str(line);
		string junk;
		Split split;
		ss >> split.id >> junk >> split.org >> junk >> split.gene;
//		cout << "Split: " << split.id << " " << split.org << " " << split.gene << endl;
		return split;
	}

	bool read_all(string filename) {
		ifstream in;
		in.open(filename.c_str());
		if (in.fail()) {
			cout << "Failed to read: " << filename << endl;
			return false;
		}
		string line;
		Split split;
		OrthoBundle bundle(org1, org2);
		vector<string> genes1;
		vector<string> genes2;
		string prev_id = "";
		while (getline(in, line)) {
			split = split_line(line);
			if (split.id != prev_id && (genes1.size() != 0 || genes2.size() != 0)) {
				// Add bundle
				bundle.genes1 = genes1;
				bundle.genes2 = genes2;
//				bundle.print();
				bundles.push_back(bundle);
				bundle = OrthoBundle(org1, org2);
				genes1.clear();
				genes2.clear();
			}
//			cout << "Split: " << split.id << " " << split.org << " " << split.gene << endl;
			if (split.org == org1) {
				genes1.push_back(split.gene);
			}
			else {
				genes2.push_back(split.gene);
			}
			prev_id = split.id;
		}
		bundle.genes1 = genes1;
		bundle.genes2 = genes2;
		bundles.push_back(bundle);
		in.close();
		return true;
	}
public:

	OrthoStream() {}

	bool open(string& organism1, string& organism2) {
		string filename = "sqltable." + organism1 + "-" + organism2;
		org1 = organism1;
		org2 = organism2;
		counter = 0;
		return read_all(filename);
	}

	bool has_next() {
		return counter != bundles.size();
	}
	
	OrthoBundle next() {
		return bundles[counter++];
	}
};

#endif
