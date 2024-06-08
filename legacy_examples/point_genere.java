// COULEUR START DELETE
import java.awt.Color;

// COULEUR STOP DELETE
/** Point modélise un point géométrique dans un plan équipé d'un
 * repère cartésien.  Un point peut être affiché et translaté.
 * Sa distance par rapport à un autre point peut être obtenue.
// DESSINER START DELETE
 * Le point peut être dessiné sur un afficheur.
// DESSINER STOP DELETE
 *
 * @author  Xavier Crégut
 * @version 1.13
 */
public class Point <(FIGURE)>extends ObjetGeometrique <(/FIGURE)>{
// NO_POINT_ATTRIBUT_FIN START DELETE
	private double x;		// abscisse
	private double y;		// ordonnée
// COULEUR START DELETE
	private Color couleur;	// couleur du point
// COULEUR STOP DELETE

// NO_POINT_ATTRIBUT_FIN STOP DELETE
	/** Construire un point à partir de son abscisse et de son ordonnée.
	 * @param vx abscisse
	 * @param vy ordonnée
	 */
	public Point(double vx, double vy) {
// FIGURE START DELETE
		super(Color.green);
// FIGURE STOP DELETE
// TRACE START DELETE
		<(TRACE_COMMENTEE)>// <(/TRACE_COMMENTEE)>System.out.println("CONSTRUCTEUR Point(" + vx + ", " + vy + ")");
// TRACE STOP DELETE
		this.x = vx;
		this.y = vy;
		this.couleur = Color.green;
	}

// CONSTRUCTEUR_COPIE START DELETE
	/** Construire un point à partir d'un autre point.
	 * @param autre l'autre point
	 */
	public Point(Point autre) {
// FIGURE START DELETE
		super(autre.getCouleur());
// FIGURE STOP DELETE
// TRACE START DELETE
		<(TRACE_COMMENTEE)>// <(/TRACE_COMMENTEE)>System.out.println("CONSTRUCTEUR COPIE Point(" + autre + ")");
// TRACE STOP DELETE
		// FIXME : afficher le point (avec ou sans this) !
		this.x = autre.x;
		this.y = autre.y;
		this.couleur = autre.couleur;
	}

// CONSTRUCTEUR_COPIE STOP DELETE
// COPIE START DELETE
	/** Obtenir une copie du point.
	 * @return une copie du point
	 */
	public Point copie() {
		return new Point(this.x, this.y);
	}

// COPIE STOP DELETE
// AVEC_COORDONNEES_POLAIRES START DELETE
// Coordonnées du point dans un repère cartésien

// AVEC_COORDONNEES_POLAIRES STOP DELETE
	/** Obtenir l'abscisse du point.
	 * @return abscisse du point
	 */
	public double getX() {
		return this.x;
	}

	/** Obtenir l'ordonnée du point.
	 * @return ordonnée du point
	 */
	public double getY() {
		return this.y;
	}

	/** Changer l'abscisse du point.
	  * @param vx nouvelle abscisse
	  */
	public void setX(double vx) {
		this.x = vx;
	}

	/** Changer l'ordonnée du point.
	  * @param vy nouvelle ordonnée
	  */
	public void setY(double vy) {
		this.y = vy;
	}

// AVEC_COORDONNEES_POLAIRES START DELETE
// Coordonnées du point dans un repère polaire

	/** Obtenir le module du point.
	  * @return le module du point
	  */
	public double getModule() {
		return Math.sqrt( Math.pow(this.getX(), 2)
						+ Math.pow(this.getY(), 2) );
	}

	/** Obtenir l'argument du point.
	  * @return l'argument du point
	  */
	public double getArgument() {
		return Math.atan2(this.getY(), this.getX());
	}

	/** Changer le module du point.
	  * @param nouveauModule le nouveau module
	  */
	public void setModule(double nouveauModule) {
		double sonArgument = this.getArgument();
		this.setX(nouveauModule * Math.cos(sonArgument));
		this.setY(nouveauModule * Math.sin(sonArgument));
	}

	/** Changer l'argument du point.
	  * @param nouvelArgument le nouvel argument
	  */
	public void setArgument(double nouvelArgument) {
		double sonModule = this.getModule();
		this.setX(sonModule * Math.cos(nouvelArgument));
		this.setY(sonModule * Math.sin(nouvelArgument));
	}

// AVEC_COORDONNEES_POLAIRES STOP DELETE
// TO_STRING START DELETE
	public String toString() {
		return "(" + this.x + ", " + this.y + ")";
	}

// TO_STRING STOP DELETE
	/** Afficher le point. */
	public void afficher() {
// TO_STRING START DELETE
		System.out.print(this);
// TO_STRING STOP DELETE
// NO_TO_STRING START DELETE
		System.out.print("(" + this.x + ", " + this.y + ")");
// NO_TO_STRING STOP DELETE
	}

	/** Distance par rapport à un autre point.
	 * @param autre l'autre point
	 * @return distance entre this et autre
	 */
	public double distance(Point autre) {
		return Math.sqrt(Math.pow(autre.x - this.x, 2)
					+ Math.pow(autre.y - this.y, 2));
	}

   /** Translater le point.
	* @param dx déplacement suivant l'axe des X
	* @param dy déplacement suivant l'axe des Y
	*/
	public void translater(double dx, double dy) {
		this.x += dx;
		this.y += dy;
	}

// AVEC_PIVOTER START DELETE
   /** Faire pivoter le point.
	* @param pivot point servant de pivot
	* @param angle angle de la rotation (en radian)
	*/
	public void pivoter(Point pivot, double angle) {
		if (this != pivot) {
			this.translater(- pivot.getX(), - pivot.getY());
			this.setArgument(this.getArgument() + angle);
			this.translater(+ pivot.getX(), + pivot.getY());
		}
	}

// AVEC_PIVOTER STOP DELETE
// DESSINER START DELETE
	/** Dessiner le point sur l'afficheur.
	 * @param afficheur l'afficheur à utiliser
	 */
	public void dessiner(afficheur.Afficheur afficheur) {
		afficheur.dessinerPoint(this.getX(), this.getY(), this.getCouleur());
	}

// DESSINER STOP DELETE
// COULEUR START DELETE
//  Gestion de la couleur

	/** Obtenir la couleur du point.
	 * @return la couleur du point
	 */
	public Color getCouleur() {
		return this.couleur;
	}

	/** Changer la couleur du point.
	  * @param nouvelleCouleur nouvelle couleur
	  */
	public void setCouleur(Color nouvelleCouleur) {
		this.couleur = nouvelleCouleur;
	}

// COULEUR STOP DELETE
// POINT_FINALIZE START DELETE
/*
	// La méthode finalize est appelée avant que le récupérateur de
	// mémoire ne détruise l'objet.  Attention toutefois, on ne sait
	// pas quand ces ressources seront libérées et il est donc
	// dangereux de s'appuyer sur ce mécanisme pour libérer des
	// ressources qui sont en nombre limité.
	//
	// D'autre part, pour être sûr que les méthodes << finalize >>
	// sont appelées avant la fermeture de Java, il faut appeler la
	// méthode statique :
	//		System.runFinalizersOnExit(true)
	//
	protected void finalize() {
		System.out.print("DESTRUCTION du point : ");
		this.afficher();
		System.out.println();
	}
*/
// POINT_FINALIZE STOP DELETE
// POINT_ATTRIBUT_FIN START DELETE

//	Représentation interne d'un point
//	---------------------------------

// Remarque : en Java, il est conseillé (convention de programmation)
// de mettre les attributs au début de la classe.

	private double x;		// abscisse
	private double y;		// ordonnée
// COULEUR START DELETE
	private Color couleur;	// couleur du point
// COULEUR STOP DELETE
// POINT_ATTRIBUT_FIN STOP DELETE

}
