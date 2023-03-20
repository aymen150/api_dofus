import pyautogui
import py.variable as v
import py.map as m
import py.dofus_action as da
import time
import requests as rq
import io
import json

def image_to_byte_file(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return {'file': img_byte_arr}

localhost = "http://127.0.0.1:8000"

rq_ressource = localhost + "/ressource"
rq_fight =  localhost + "/fight"
rq_consommable =  localhost + "/consommable"
rq_fight_en_cours =  localhost + "/fight/en_cours"

#choise "Bonta" : "Amakna" : "Sufokia" : "Pandala" : "Koalak" : "Otomai"
region_banque = "Koalak"
pos_banque = v.pos_banque_koalak
#choise : "amakna sud" : "foret bonta" : "dragoeuf" : "pandala sud" : "koalak" : "otomai"
region_parcours = "koalak"


print("""
    !!! NE PAS OUBLIER !!!
- Mode créature en combat
- dragodinde équipé
- Energie dragodinde
- Onglet potion trier par ordre alphabétique
      """)

print("""
      ######################################
      #######   S   T   A   R   T   #########
      #######################################
      """)
time.sleep(3)
pos_joueur = da.coordonnées_joueur((500,500))
a = 0
first_fight = True 
circuit = m.circuit(region_parcours) 
while True : 
    numero_map = 0
    for map in circuit :                      # pour chaque map du parcours
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time)
        time.sleep(1)
                                                   #lecture ocr de la map actuelle
        map_actuelle = da.my_map()
        if map_actuelle == "999,999" :
            print("error detecting map")
            map_actuelle = map.map 
        elif not da.eguals_map(map_actuelle, map.map) :  
                              # verifier que la map actuelle en jeu est bien la map sur laquel on travaille
            print("map théorique :", map.map, "map pcr : ", map_actuelle)
            dist = da.distance_map(map_actuelle,map.map)
            if dist < 35 :
                da.travel(map.map,dist*10)
            else :
                print("travel trop long")
        list_bounding_click = []
        list_recolte = []
        list_bounding_deja_cliquer = []
        indice = 0
        while len(list_bounding_click) > 0 or indice == 0 :
            indice += 1
            pyautogui.keyDown("y")                         #surbrillance des ressources de la map en cours
            time.sleep(0.15)
            image = pyautogui.screenshot(region=v.region_gameplay)  #screenshot de la region de jeu
            pyautogui.keyUp("y")                            # fin de surbrillance
            w,h = image.size
        
            # detection des IA ressources
            response =  rq.get(rq_ressource , files=image_to_byte_file(image))
            predictions = response.json()
            # liste des zones boxes des ressources
            list_bounding_click_tmp =  da.predictions_to_click(predictions,w,h,proba_poisson=0.3,proba_plante=0.5,proba_bois=0.33)
            list_bounding_click = [elem for elem in list_bounding_click_tmp if elem[1] not in list_recolte] 
            print("recherche ressource")
            if len(list_bounding_click) > 0 :
                list_bounding_click_desordonne = da.list_click_filter(list_bounding_click)    # filtre les positions pour eviter un changement de map
                if len(list_bounding_click_desordonne) > 0 :
                    bounding_click = da.minDistance(pos_joueur,list_bounding_click_desordonne)
                    bounding, click = bounding_click
                    list_recolte.append(click)
                    pos_joueur = click
                    print(f"map : {map.map}, ressource : {click}")
                    while da.is_connected == False :
                        time.sleep(30)
                        #da.connexion() 
                    x,y = click
                    if da.click_in_list_bounding((x,y),list_bounding_deja_cliquer) == False : 
                        da.dofus_click(x,y,0.1,4)                 # recolte de la ressources
                        print("click ", x,y)
                        list_bounding_deja_cliquer.append(bounding)
                else :
                    break
                    
            response =  rq.get(rq_fight_en_cours , files=image_to_byte_file(image))
            classification = response.json()
            if classification != "monde" :
                print("debut combat")
                print("-- prendre du pain")
                da.manger_du_pain(10)
                print("-- pain mangé")
                time.sleep(0.2)
                if first_fight :
                    first_fight = False
                    da.mode_creature()
                pyautogui.press("f1")
            
                while classification != "monde"  :
                    if da.my_tourn() == True :
                        image_fight = pyautogui.screenshot(region=v.region_gameplay)
                        w_f,h_f = image_fight.size
                        response = rq.get(rq_fight , files=image_to_byte_file(image_fight))
                        predictions_fight = response.json()
                        da.combat(predictions_fight,w_f,h_f)
                    else :
                        time.sleep(2)
                    response =  rq.get(rq_fight_en_cours , files=image_to_byte_file(pyautogui.screenshot(region=v.region_gameplay)))
                    classification = response.json()
                time.sleep(3)
                da.dofus_press("enter",3)
                print("fin du combat")
               
        time.sleep(3)
        
        # deplacement du personnage jusqu'a la prochaine map de recolte
        pos = (map.next_map.x, map.next_map.y)
        x,y = pos
        print("changement de map")
        da.dofus_click(x,y,0.3,0)
        pos_joueur = da.coordonnées_joueur(pos)
        numero_map += 1
        numero_map = numero_map if numero_map < len(circuit) else 0
        da.changement_map(pyautogui.screenshot(region = v.region_map ), map.next_map, circuit[numero_map].map)
        print("fin changement de map")
        print("_____________________________________")
    
    # une fois le parcours fini direction la banque amakna déposer les ressources
    #a += 1
    #if (a%1) == 0 :
    da.go_bank(my_pos = map_actuelle , region  = region_banque )
    response = rq.get(rq_consommable , files=image_to_byte_file(pyautogui.screenshot(region = v.region_onglet_ressource )))
    nb_potion = response.json()
    da.transfert_coffre_ressource("ressource",30)
    da.transfert_coffre_ressource("potion", nb_potion-4)
    da.fermer_coffre_guilde()
    da.travel(circuit[0].map, da.distance_map(circuit[0].map,pos_banque)) #retour au point de départ du parcours
    #da.travel("-1,24",da.distance_map("2,-2","-1,24")) #retour au point de départ du parcours

