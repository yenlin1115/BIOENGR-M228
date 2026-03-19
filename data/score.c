/* file: score.c   Ikaro Silva and George Moody  30 July 2012   version 1.4

Calculate scores for Challenge 2012

This program accepts a pair of text files:
  results    (3-column file of outputs from a challenge entry)
  outcomes   (known outcomes for the patients)

Its output is a pair of scores (the minimum of Se and PPV for event 1, and
the normalized Hosmer-Lemeshow H statistic for event 2).

Compile it with the standard C math library;  using gcc, do this by
    gcc -o score score.c -lm

If you have created a results file for set A named 'Outputs-a.txt', and
you have downloaded the known outcomes ('Outcomes-a.txt'), calculate
the scores using the command:
    score Outputs-a.txt Outcomes-a.txt >scores-a.txt
(which will save the calculated scores in a file named 'scores-a.txt').

The results for each risk decile are written to the standard error output
in three columns (centroid of risk for the decile, number of observed deaths
of patients in the decile, and number of predicted deaths in the decile).
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define N 4000  /* Number of records in each data set */
#define D 10    /* Use deciles to calcuate lemeshow values */
#define M (N/D)	/* Number of records per decile */

#define VERBOSE	/* comment out this line for compact output */

int rowcmp(const void *a, const void *b)
{
    double *riska = (double *)a + 2, *riskb = (double *)b + 2;

    if (*riska < *riskb) return (-1);
    if (*riska > *riskb) return (1);
    if (*((double *)a) < *((double *)b)) return (-1);
    if (*((double *)a) > *((double *)b)) return (1);
    return (0);
}

main(int argc, char **argv)
{
    char buf[128];
    int i, RecordID, survival, R2, a1, a2, a3, a4, IHD;
    double risk, tp = 0, fn = 0, fp = 0, se = 0, ppv = 0, h = 0,
	centroid = 0, obs = 0, exp = 0, htemp = 0, drmin, drrange;
    static double r[N][4]; 
    /* r is an Nx4 array.  Each row will contain a RecordID, survival, risk,
       and IHD for one of the 4000 patients in the data set. */
    FILE *results, *outcomes;

    if (argc != 3) {
	fprintf(stderr, "Usage: score results outcomes\n");
	exit(1);
    }
    if ((results = fopen(argv[1],"r")) == NULL) {
	fprintf(stderr, "%s: can't open %s\n", argv[0], argv[1]);
	exit(1);
    }
    if ((outcomes = fopen(argv[2],"r")) == NULL) {
	fprintf(stderr, "%s: can't open %s\n", argv[0], argv[2]);
	exit(1);
    }

    /* Read the input files into r_id */

    /* read and ignore the column headings in the outcomes file */
    fgets(buf, sizeof(buf), outcomes);
    for (i = 0; i < N; i++) {
	if (fscanf(results, "%d,%d,%lf", &RecordID, &survival, &risk) != 3 ||
	    fscanf(outcomes, "%d,%d,%d,%d,%d,%d", &R2, &a1, &a2, &a3, &a4, &IHD)
	    != 6 || RecordID != R2) {
	    fprintf(stderr, "Improper input for line %d (record %d in %s, "
		    "or record %d in %s)\n", i, RecordID, argv[1], R2, argv[2]);
	    fclose(results);
	    fclose(outcomes);
	    exit(1);
	}

	r[i][0] = RecordID;
	r[i][1] = survival;
	r[i][2] = risk;
	r[i][3] = IHD;
     }
    fclose (results);
    fclose (outcomes);

    qsort(r, N, 4*sizeof(double), &rowcmp);	/* sort rows by risk */
 
    for (i = 0; i < N; i++) {
	if (r[i][3]) {	/* observed death */
	    tp += r[i][1];
	    fn += (!r[i][1]);
	    obs++;
	}
	else 	/* observed survival */
	    fp += r[i][1];
	centroid += r[i][2];
	if ((i+1) % M  ==  0) {  /* we have now accumulated data for a decile */
	    centroid /= M;
	    if (i+1 == M) drmin = centroid;  /* save risk for decile 1 */
	    else if (i+1 == N) drrange = centroid - drmin;
	    exp = M*centroid;
	    htemp = (obs-exp)*(obs-exp) / 
		(M * (centroid*(1 - centroid) + 0.001));
	    /* The 0.001 is to avoid division by zero if centroid is 0 or 1 */
	    h += htemp;
	    /* Save decile stats for plotting. */
	    fprintf(stderr, "%g %g %g\n", centroid, obs, exp);

	    /* Reset stats for the next decile */
	    centroid = 0;
	    obs = 0;
	}
    }

    se = tp/(tp+fn);
    ppv = tp/(tp+fp);

#ifdef VERBOSE
    printf("Se = %g, PPV = %g\n", se, ppv);
    printf("Unofficial Event 1 score: %g\n", (se < ppv) ? se : ppv);
    printf("Unofficial Event 2 score: %g\n", h/drrange);
#else
    printf("%g,%g\n", (se<ppv) ? se : ppv, h/drrange); 
#endif

    exit(0);
}
