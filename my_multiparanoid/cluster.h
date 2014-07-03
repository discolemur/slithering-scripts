#ifndef _CLUSTER
#define _CLUSTER

using std::map;
using std::string;
using std::set;
using std::vector;
using std::ostream;
using std::endl;

class Cluster {

private:
	// Map from organism to genes
	map<string, set<string> > data;

public:
	Cluster() {}

	// Put the gene into the organism
	void add(string& organism, string& gene) {
		if (data.find(organism) == data.end()) {
			data[organism] = set<string>();
		}
		data[organism].insert(gene);
	}
	
	void add(string& organism, vector<string>& genes) {
		for (int i = 0; i < genes.size(); ++i) {
			data[organism].insert(genes[i]);
		}
	}

	// If we found the gene, we can add all genes associated with that gene to this cluster.
	bool find_gene(string& organism, string& gene) {
		if (data.find(organism) == data.end()) {
			return false;
		}
		return data[organism].count(gene);
	}

	void write(ostream& out, int id) {
		map<string, set<string> >::iterator it = data.begin();
		while (it != data.end()) {
			string organism = it->first;
			set<string> genes = it->second;
			for (set<string>::iterator gene_ptr = genes.begin(); gene_ptr != genes.end(); gene_ptr++) {
				out << id << "\t" << organism << "\t" << *gene_ptr << endl;
			}
			it++;
		}
	}
};

#endif
