with Ada.Text_IO;              use Ada.Text_IO;
with Piles;<(NO_GENERIQUE)>     use Piles;<(/NO_GENERIQUE)>

procedure Afficher_Entier is

	-- marqueur afficher.spec START DELETE
	-- Afficher un entier naturel sur la sortie standard.
	procedure Afficher (N : in Integer) with
		Pre => N >= 0
	-- marqueur afficher.spec STOP DELETE
	is
	-- GENERIQUE START DELETE
		package Piles_Character is
			new Piles (<(TABLEAU)>Integer'Width, <(/TABLEAU)>Character);
		use Piles_Character;

	-- GENERIQUE STOP DELETE
		Nombre   : Integer;       -- le nombre à afficher (copie de N)
		Unite    : Integer;       -- un chiffre de Nombre
		Chiffre  : Character;     -- le caractère correspondant à Unite.
		Chiffres : T_Pile;        -- les chiffres de Nombre

	begin
		-- Empiler les chiffres de l'entier
		Initialiser (Chiffres);
		Nombre := N;
		loop
			-- récupérer le chiffre des unités
			Unite := Nombre Mod 10;

			-- le convertir en un caractère
			Chiffre := Character'Val (Character'Pos('0') + Unite);

			-- l'empiler
-- TABLEAU START DELETE
			pragma Assert (not Est_Pleine (Chiffres));
-- TABLEAU STOP DELETE
			Empiler (Chiffres, Chiffre);

			-- réduire le nombre en supprimant les unités
			Nombre := Nombre / 10;
		exit when Nombre = 0;
		end loop;
		pragma Assert (Nombre = 0);
		pragma Assert (not Est_Vide (Chiffres));

		-- Afficher les chiffres de la pile
		loop
			-- Obtenir le chiffre en sommet de pile
			Chiffre := Sommet (Chiffres);

			-- afficher le caractère
			Put (Chiffre);

			-- supprimer le caractère de la pile
			Depiler (Chiffres);
		exit when Est_Vide (Chiffres);
		end loop;
-- CHAINEE START DELETE

		Detruire (Chiffres);
-- CHAINEE STOP DELETE
	end Afficher;



begin
	Put ("10 = ");
	Afficher (10);
	New_Line;

	Put ("0 = ");
	Afficher (0);
	New_Line;

	Put ("Integer'Last = ");
	Afficher (Integer'Last);
	New_Line;
end Afficher_Entier;
