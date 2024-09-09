from pyspigot.plugin import Plugin, event, command
import random

class FightingGame(Plugin):
    def on_enable(self):
        self.logger.info("Fighting Game plugin has been enabled!")
        self.players = {}
        self.abilities = {
            "Dash": self.dash,
            "Fireball": self.fireball,
            "Heal": self.heal
        }
        self.spawn_location = [0, 64, 0]  # Example spawn location

    def on_disable(self):
        self.logger.info("Fighting Game plugin has been disabled!")

    @command(name="join", description="Join the Fighting Game", usage="/join")
    def join_command(self, sender, command, label, args):
        player = sender.get_player()
        if player:
            abilities = random.sample(list(self.abilities.keys()), 2)
            self.players[player.get_unique_id()] = abilities
            player.send_message(f"You joined the Fighting Game with abilities: {abilities[0]} and {abilities[1]}")
            player.teleport(self.spawn_location)
            self.equip_player(player)

    @command(name="leave", description="Leave the Fighting Game", usage="/leave")
    def leave_command(self, sender, command, label, args):
        player = sender.get_player()
        if player and player.get_unique_id() in self.players:
            del self.players[player.get_unique_id()]
            player.send_message("You have left the Fighting Game!")

    def equip_player(self, player):
        # Clear inventory and give basic equipment
        player.get_inventory().clear()
        player.get_inventory().add_item(self.get_server().create_item_stack("DIAMOND_SWORD", 1))
        player.get_inventory().add_item(self.get_server().create_item_stack("GOLDEN_APPLE", 5))

    @event("player.PlayerDropItemEvent")
    def on_player_drop_item(self, event):
        player = event.getPlayer()
        if player.get_unique_id() in self.players:
            event.setCancelled(True)
            ability = self.players[player.get_unique_id()][0]
            self.abilities[ability](player)

    @event("player.PlayerInteractEvent")
    def on_player_interact(self, event):
        player = event.getPlayer()
        if player.get_unique_id() in self.players and event.getAction().name().startswith("RIGHT_CLICK"):
            ability = self.players[player.get_unique_id()][1]
            self.abilities[ability](player)

    def dash(self, player):
        location = player.get_location()
        direction = location.get_direction().normalize().multiply(5)
        new_location = location.add(direction)
        player.teleport(new_location)
        player.send_message("You dashed forward!")

    def fireball(self, player):
        player.launch_projectile("Fireball")
        player.send_message("You launched a fireball!")

    def heal(self, player):
        health = player.get_health()
        max_health = player.get_max_health()
        heal_amount = 5
        new_health = min(health + heal_amount, max_health)
        player.set_health(new_health)
        player.send_message("You healed yourself!")

    @event("player.PlayerRespawnEvent")
    def on_player_respawn(self, event):
        player = event.getPlayer()
        if player.get_unique_id() in self.players:
            self.equip_player(player)
            player.teleport(self.spawn_location)

plugin = FightingGame()