#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <fstream>
#include <sstream>
#include "cluster.h"
#include "orthobundle.h"
#include "orthostream.h"

using namespace std;

/*
 * This program needs to combine predicted clusters from inparanoid output
 * Algorithm:
 * 	Put the first file into clusters.
 * 	Open the next file, put into clusters. If no cluster takes it, make a new cluster.
 * 	Continue.
 */

void put_all_in_cluster(Cluster& cluster, OrthoBundle& bundle) {
	cluster.add(bundle.organism1, bundle.genes1);
	cluster.add(bundle.organism2, bundle.genes2);
}

void handle_bundle(vector<Cluster>& clusters, OrthoBundle& bundle) {
	for (int i = 0; i < clusters.size(); ++i) {
		// Search for the first organism's genes
		for (int j = 0; j < bundle.genes1.size(); j++) {
			if (clusters[i].find_gene(bundle.organism1, bundle.genes1[j])) {
				put_all_in_cluster(clusters[i], bundle);
				return;
			}
		}
		// Search for the second organism's genes
		for (int j = 0; j < bundle.genes2.size(); j++) {
			if (clusters[i].find_gene(bundle.organism2, bundle.genes2[j])) {
				put_all_in_cluster(clusters[i], bundle);
				return;
			}
		}
	}
	// No cluster could take it, so we make a new cluster.
	Cluster c;
	put_all_in_cluster(c, bundle);
	clusters.push_back(c);
}

void write_output(vector<Cluster>& clusters) {
	ofstream out;
	out.open("clusters.discolemur");
	out << "ClusterID\tOrganism\tGeneID" << endl;
	for (int i = 0; i < clusters.size(); ++i) {
		clusters[i].write(out, i);
	}
}

vector<string> parse_arg(char* orgs) {
	string concat(orgs);
	vector<string> list;
	string next = "";
	cout << "Interpreted list of organisms:" << endl;
	for (int i = 0; i < concat.size(); ++i) {
		if (concat[i] == '+') {
			cout << "\t" << next << endl;
			list.push_back(next);
			next = "";
		}
		else {
			next.push_back(concat[i]);
		}
		if (i == concat.size() - 1) {
			cout << "\t" << next << endl;
			list.push_back(next);
		}
	}
	return list;
}

int main(int argc, char* argv[]) {
	if (argc != 2) {
		cout << "Usage: ";
		cout << argv[0];
		cout << " sp1+sp2+...+sp3" << endl;
		return 1;
	}
	vector<string> organisms = parse_arg(argv[1]);
	vector<Cluster> clusters;
	string model_org, model_gene, organism, gene;
	OrthoStream orthostream;
	for (int i = 0; i < organisms.size(); ++i) {
		for (int j = 0; j < organisms.size(); ++j) {
			if (i == j) continue;
			if (!orthostream.open(organisms[i], organisms[j])) {
				continue;
			}
			while (orthostream.has_next()) {
				OrthoBundle bundle = orthostream.next();
				handle_bundle(clusters, bundle);
			}
		}
	}
	write_output(clusters);
	return 1;
}
