boss_name_hp_map: dict[str, int] = {"Garub": 140_000, "Inachaus": 170_000, "Black'ist": 210_000, "Trenun": 260_000, "Sedulus Rane": 415_000, "Serezith Brakrud": 515000}
player_dps_dict = {"Player1": 0, "Player2": 0, "Player3": 200, "Player4": None, "Player5": None}
desired_completion_time_s = int(input("Enter desired completion time in seconds: "))
number_of_uncertain_player_dps = list(player_dps_dict.values()).count(None)

for boss, hp in boss_name_hp_map.items():
    print(f"Boss Name: {boss}")
    total_boss_dps = hp / desired_completion_time_s
    print(f"Total boss dps is {total_boss_dps}")

    # works on all the custom damage entered for the players
    for player, dps in player_dps_dict.items():
        if dps is not None:
            total_boss_dps -= dps
            print(f"{player} dps is {dps}")

    for player, dps in player_dps_dict.items():
        if dps is None:
            player_dps = total_boss_dps / number_of_uncertain_player_dps
            print(f"{player} dps is {player_dps}")

    print("\n")
