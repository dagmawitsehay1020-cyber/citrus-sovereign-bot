from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import string
import asyncio
import os
import threading
from flask import Flask

web_app = Flask(__name__)

@web_app.route('/')
def health_check():
    return "🍋 Citrus Sovereign is running!"

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

MESSAGES = {
    "join_full": [
        "🍋 Tree's full, sourpuss. Max 4 players. Try again later.",
        "👨‍🌾 Lemonade stand is packed – no room for you!",
        "💔 Full harvest! Come back next season.",
        "🪑 No more branches to sit on. This orchard is full."
    ],
    "already_in_game": [
        "🤨 You're already squeezing lemons in another game. Finish first!",
        "😏 One citrus war at a time, greedy guts.",
        "🔄 You can't be in two orchards at once. Focus!",
        "❌ Already scheming elsewhere. Come back when you're done."
    ],
    "game_started": [
        "<b>🍋 CITRUS SOVEREIGN BEGINS!</b> 🍋\nEveryone gets <b>100 lemons</b>. May the juiciest win.",
        "<b>🍋 100 lemons each!</b> Let the zesty backstabbing begin.",
        "<b>🏁 And they're off!</b> First round incoming. Hold onto your lemons.",
        "<b>⚡ Game active!</b> Try not to get squeezed out in round 1."
    ],
    "round_start": [
        "<b>✨ Round {round_num} begins!</b> \nThe chest contains <b>{chest} Crowns</b>. \n<i>Choose your bid below (You have 60 seconds):</i> ",
        "<b>🔔 Ding ding! Round {round_num}.</b> {chest} Crowns up for grabs. \n<i>Tap a button to bid your lemons. You have been given 60 seconds to submit a bid.</i>",
        "<b>🎲 Shake those lemons!</b> Round {round_num} – \n<b>{chest} Crowns</b> in the basket. \n<i>Bid now within the next 60 seconds!</i>",
        "<b>⏰ Round {round_num}!</b> Don't be slow... you only have a minute. Pick a bid amount. This pay out for this round is <b>{chest} Crowns</b>"
    ],
    "already_bid": [
        "<b>🙅 You already bid this round.</b> Wait for results!",
        "<b>😤 Patience!</b> One bid per round.",
        "<b>⏳ Already in the system.</b> No double squeezing!",
        "<b>🤦‍♀️ Tried to bid again?</b> Nice try, but no."
    ],
    "no_round_active": [
        "<b>⏸ No active round.</b> Next one starts automatically!",
        "<b>🛑 Chill</b> – round hasn't started yet.",
        "<b>⌛ Wait for the next round, hotshot.</b>"
    ],
    "round_result_win": [
        "<b>🏆 Highest bid: {highest_bid} lemons.</b> Winner gets <b>{vp} Crowns</b>! 👑",
        "<b>🎉 The winner wins with {highest_bid} lemons</b> – takes <b>{vp} Crowns</b>!",
        "<b>💪 Victory!</b> {highest_bid} lemons was the magic number. <b>+{vp} Crowns</b>."
    ],
    "round_result_tie": [
        "<b>🤝 Tie at {highest_bid} lemons.</b> No crowns for anyone!",
        "<b>😐 Everyone bid the same</b> – no winners this round.",
        "<b>⚖️ Birds of a feather...</b> no crowns awarded."
    ],
    "game_over_win": [
        "<b>🏆 GAME OVER!</b> {winner} is the Citrus Sovereign with <b>{vp} Crowns</b>! 👑🍋",
        "<b>💀 Game over!</b> {winner} takes the crown with <b>{vp} Crowns</b>. Respect.",
        "<b>🎊 And the new Citrus Sovereign is...</b> {winner} with <b>{vp} Crowns</b>! Well played."
    ],
    "game_over_tie": [
        "<b>🤝 TIE!</b> {winners} each have <b>{vp} Crowns</b>. Share the throne?",
        "<b>⚖️ It's a draw!</b> {winners} end with <b>{vp} Crowns</b>. Rematch?",
        "<b>😐 Deadlock</b> – {winners} share the crown with <b>{vp} Crowns</b> each."
    ],
    "welcome": [
        "🍋 Welcome to <b>Citrus Sovereign</b>! Ready to squeeze your way to the crown? Type /newgame to create a lobby. 👑",
        "🤑 Hey there, future sovereign! /newgame starts your own citrus empire.",
        "👑 Future Majesty! Citrus Sovereign awaits. Use /newgame to begin your zesty adventure.",
        "💎 Welcome, lemon lord! /newgame – let the citrus scheming commence."
    ],
    "already_started_join": [
        "🚫 Too late, juicebag! This game already started. Better luck next time. 🤷",
        "⏰ Game's already rolling. You can't join now.",
        "🏁 The lemon train has left the station. No boarding after start."
    ],
    "self_join": [
        "🧐 You're already in this game. Trying to clone yourself? 😏",
        "🤨 You're already here. One sour face is enough.",
        "😎 You're on the list already. Pat yourself on the back."
    ],
    "not_in_lobby": [
        "❓ You're not in any lobby. Type /newgame to start your own citrus war.",
        "😕 No lobby found for you. Create one with /newgame.",
        "🕵️‍♂️ I see no game with your name. /newgame is your friend."
    ],
    "game_already_started": [
        "🏁 Game already started. Too late to squeeze in!",
        "🚀 Already active. Can't start twice!",
        "🎲 The lemons are rolling – game already began."
    ],
    "need_more_players": [
        "😢 Need at least 2 players to start. Invite more citrus addicts! 😈",
        "👥 Only one player? That's a sad lemon party. Get a friend.",
        "🤷‍♂️ Can't start a citrus war alone. Bring at least one more."
    ],
    "already_in_match_start": [
        "❌ Hold your horses! You're already in a game. Finish or forfeit before starting another. 🐎",
        "🔄 One citrus battle at a time! You're already busy.",
        "😤 You're already playing. Focus on that one!"
    ],
    "not_in_active_game_bid": [
        "😵 You're not in an active game. Type <code>/newgame</code> to start your own citrus saga. 🎲",
        "🤔 No active game found. <code>/newgame</code> is your ticket.",
        "🚫 You're not playing anything right now. Start a game first."
    ],
    "status_lobby": [
        "<b>🍋 Game:</b> <code>{game_id}</code> (Lobby)\n<b>👥 Players:</b> {players}\n<b>⏳ Status:</b> Waiting for /game_start\n<i>Go on, poke your friends!</i> 😏",
        "<b>🃏 Lobby</b> <code>{game_id}</code> – {players} waiting. Type <code>/game_start</code> when ready.",
        "<b>🍻 Pre‑game citrus stand!</b> {players} inside. Kick it off with <code>/game_start</code>."
    ],
    "status_active": [
        "<b>🍋 Game:</b> <code>{game_id}</code>\n<b>👥 Players:</b> {player_count}\n<b>🔁 Round:</b> {round_display}\n<b>🍋 Your lemons:</b> {gold}\n<b>👑 Your Crowns:</b> {vp}\n<i>Keep your friends close and your enemies closer.</i> 🔪",
        "<b>📊 Active game</b> <code>{game_id}</code> – Round {round_display}. You have {gold} lemons, {vp} crowns.",
        "<b>⚔️ In the thick of it!</b> Game <code>{game_id}</code>, round {round_display}. Lemons: {gold}, Crowns: {vp}."
    ],
    "added_gold": [
        "<b>✨ Ka-ching!</b> Added {amount} lemons. Now you have <b>{new_gold} lemons</b>. Feeling zesty? 🍋",
        "<b>💰 +{amount} lemons!</b> Your stash: {new_gold} lemons.",
        "<b>💸 Generous!</b> {amount} lemons added. Total: {new_gold} lemons."
    ],
    "removed_gold": [
        "<b>💸 Poof!</b> Removed {amount} lemons. You now have <b>{new_gold} lemons</b>. Hope it was worth it. 😬",
        "<b>😭 -{amount} lemons.</b> Balance: {new_gold} lemons.",
        "<b>🪦 Ouch!</b> Lost {amount} lemons. Left with {new_gold}."
    ],
    "remove_insufficient": [
        "<b>❌ You only have {current} lemons.</b> Trying to squeeze me? Nice try. 🚫",
        "<b>😤 Insufficient lemons!</b> You have {current}, need {amount}.",
        "<b>🤡 You don't have that many lemons.</b> Balance: {current}."
    ],
    "gold_command": [
        "<b>🍋 Your zesty lemon stash:</b> <code>{gold}</code> 🍋\n<i>Squeeze them wisely... or don't, I'm not your mom.</i>",
        "<b>🪙 You're sitting on {gold} lemons.</b> Use them or lose them!",
        "<b>💎 Current lemons: {gold}.</b> Make lemonade... or hoard."
    ],
    "no_gold_start": [
        "🤨 You haven't even started! Send /start first, you silly citrus. 🍊",
        "😐 No lemons yet? Send /start to begin your journey.",
        "🪄 You need to /start before checking your lemons."
    ],
    "final_summary": [
        "<b>🏆 CITRUS SOVEREIGN FINAL TALLY</b> 🏆\n\n{summary}",
        "<b>📊 Game over!</b> Here's how the crown was won:\n\n{summary}",
        "<b>🎬 That's all folks!</b> Final citrus scoreboard:\n\n{summary}"
    ],
    "bid_button_press": [
        "<b>🍋 You bid {bid} lemons.</b> Zesty move!",
        "<b>💸 {bid} lemons, huh?</b> Let's see if it pays off in crowns.",
        "<b>🤞 Bid of {bid} recorded.</b> Fingers crossed!",
        "<b>📝 {bid} lemons in the pot.</b> Waiting for others..."
    ]
}

CHARACTERS = {
    "Merchant": {
        "buff": {"starting_lemons": 15}, 
        "debuff": {"lose_lemon_on_win": 5}, 
        "description": "💰 Starts with +15 lemons. 👑 Loses 5 lemons every time you win."
    },
    "Noble": {
        "buff": {"bonus_crowns_on_high_chest": 5, "high_chest_threshold": 40}, 
        "debuff": {"lose_extra_on_loss": 5}, 
        "description": "👑 +5 bonus crowns for winning a 40+ chest. 💸 Lose 5 extra lemons on a loss."
    },
    "Usurper": {
        "buff": {"steal_on_win": 10}, 
        "debuff": {"lose_extra_on_loss": 10}, 
        "description": "🍋 Steal 10 lemons from the richest player on a win. 💸 Lose 10 extra lemons on a loss."
    },
    "Cultist": {
        "buff": {"gain_vp_on_loss": 5}, 
        "debuff": {"lose_lemon_on_win": 10}, 
        "description": "🧙 Gain 5 crowns for every round you lose. 🔥 Lose 10 lemons when you win."
    },
    "Gambler": {
        "buff": {"roll_bonus": True}, 
        "debuff": {"min_bid": 10}, 
        "description": "🎲 Roll 1‑5 → gain roll×5 lemons. 🚫 Minimum bid is 10 lemons (no 0 or 5)."
    },
    "Broker": {
        "buff": {"gain_half_on_tie": True},
        "debuff": {"gap_bn_next": 15, "lose_lemon": 5}, 
        "description": "🤝 Gain half the chest if you tie for the win. 💸 Lose 5 lemons if your bid is more than 10 away from the nearest opponent."
    },
    "Spy": {
        "buff": {"see_lowest_bid": True},
        "debuff": {"gap_bn_winner": 10, "lose_lemon": 5}, 
        "description": "🕵️ See the lowest bid before you bid. 💸 Lose 5 lemons if your bid is more than 10 away from the highest bid."
    },
}
 
HELP_PAGES = {
    "overview": {
        "title": "🍋 Welcome to Citrus Sovereign!",
        "text": (
            "<b>Goal:</b> Become the Citrus Sovereign by collecting the most 👑 <b>Crowns</b>.\n\n"
            "You spend 🍋 <b>Lemons</b> to bid on treasure chests. Each chest contains a random number of Crowns.\n\n"
            "Win the chest by placing the <b>highest bid</b> – but beware: <i>everyone loses the lemons they bid, win or lose!</i>\n\n"
            "After 5 rounds, the player with the most Crowns rules the citrus kingdom."
        )
    },
    "setup": {
        "title": "🏛️ Setting Up a Game",
        "text": (
            "1️⃣ Type <code>/newgame</code> to create a lobby.\n"
            "2️⃣ Share the link the bot gives you with 1‑3 friends.\n"
            "3️⃣ Friends click the link and type <code>/game_start</code> when ready.\n\n"
            "Only the <b>game creator</b> can start the match.\n"
            "You can also <code>/leave</code> the lobby before the game begins."
        )
    },
    "bidding": {
        "title": "🃏 Bidding",
        "text": (
            "Each round, you'll see a message with <b>inline buttons</b>:\n"
            "• 0, 5, 10, 15, … up to your current 🍋 lemons.\n"
            "• ⏰ You have 60 seconds to bid. After that, you auto‑bid 0.\n"
            "After you bid, the bot shows how many players have bid and how many remain.\n\n"
            "<i>Gambler</i> minimum bid is 10 lemons (no 0 or 5)."
        )
    },
    "characters": {
        "title": "🎭 Characters",
        "text": (
            "Each player gets a <b>random character</b> – all unique!\n\n"
            "🛒 <b>Merchant</b> – +15 lemons, but lose 5 on a win.\n"
            "👑 <b>Noble</b> – bonus crowns for high chests (40+), lose 5 on a loss.\n"
            "🍋 <b>Usurper</b> – steal 10 lemons on a win, lose 10 on a loss.\n"
            "🧙 <b>Cultist</b> – gain 5 crowns on a loss, lose 10 on a win.\n"
            "🎲 <b>Gambler</b> – roll ×5 extra lemons, minimum bid 10.\n"
            "🤝 <b>Broker</b> – gain half chest on tie, lose 5 if far from pack.\n"
            "🕵️ <b>Spy</b> – see the lowest bid, lose 5 if too far from winner. <i> Only available in 2+ player lobbies</i>"
        )
    },
    "scoring": {
        "title": "🏆 Rounds & Scoring",
        "text": (
            "• <b>5 rounds</b> total.\n"
            "• Each chest has <b>10–60 Crowns</b> (random).\n"
            "• Winner = highest unique bid. If tie, <b>no one</b> gets the chest (unless you're a <i>Broker</i> – you get half!).\n"
            "• All players <b>lose the lemons</b> they bid.\n"
            "• Character buffs and debuffs trigger automatically.\n\n"
            "After round 5, the bot calculates the final scores and declares a winner!"
        )
    },
    "commands": {
        "title": "📜 Command Reference",
        "text": (
            "<code>/newgame</code> – Create a lobby.\n"
            "<code>/game_start</code> – Start the game (creator only).\n"
            "<code>/status</code> – Check your lemons, crowns, and round.\n"
            "<code>/leave</code> – Leave the game (lobby or mid‑game).\n"
            "<code>/stopgame</code> – Force‑end the game (creator only).\n"
            "<code>/help</code> – Open this guide.\n\n"
            "<i>All commands work in your DM with the bot.</i>"
        )
    }
}

HELP_ORDER = ["overview", "setup", "bidding", "characters", "scoring", "commands"]


def get_random_message(category, **kwargs):
    choices = MESSAGES.get(category, [f"⚠️ No message for category: {category}"])
    msg = random.choice(choices)
    return msg.format(**kwargs)

user_lemons = {}      # solo player lemons (for testing)
user_game = {}        # user_id -> game_id
games = {}            # game_id -> game dict

async def get_username(context, user_id):
    try:
        chat = await context.bot.get_chat(user_id)
        return f"@{chat.username}" if chat.username else f"User{user_id}"
    except:
        return f"User{user_id}"

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    if user_id in user_game:
        await update.message.reply_text(get_random_message("already_in_game"), parse_mode='HTML')
        return
    payload = context.args[0] if context.args else None

    if payload and payload in games:
        game = games[payload]
        if game["status"] != "lobby":
            await update.message.reply_text(get_random_message("already_started_join"), parse_mode='HTML')
            return
        if user_id in game["players"]:
            await update.message.reply_text(get_random_message("self_join"), parse_mode='HTML')
            return
        if len(game["players"]) >= 4:
            await update.message.reply_text(get_random_message("join_full"), parse_mode='HTML')
            return

        game["players"].append(user_id)
        game["usernames"][user_id] = await get_username(context, user_id)
        game["lemons"][user_id] = None
        user_game[user_id] = payload
        player_list = ", ".join([game["usernames"].get(pid, str(pid)) for pid in game["players"]])
        joiner_name = await get_username(context, user_id)
        for pid in game["players"]:
            if pid != user_id:
                await context.bot.send_message(
                    pid,
                    f"🍋 <b>{joiner_name}</b> has joined the lobby! Current players: {len(game['players'])}/4.",
                    parse_mode='HTML'
                )
        await update.message.reply_text(
            f"🍋 Welcome aboard, {await get_username(context, user_id)}! You joined game {payload}.\n👥 Current crew: {player_list}\n⚡ Type /game_start when ready to rumble!",
            parse_mode='HTML'
        )
        return

    await update.message.reply_text(get_random_message("welcome"), parse_mode='HTML')

async def lemons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    if user_id not in user_lemons:
        await update.message.reply_text(get_random_message("no_gold_start"), parse_mode='HTML')
        return
    lemons = user_lemons[user_id]
    await update.message.reply_text(get_random_message("gold_command", gold=lemons), parse_mode='HTML')

async def add_lemons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    if user_id not in user_lemons:
        await update.message.reply_text(get_random_message("no_gold_start"), parse_mode='HTML')
        return
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("📢 Usage: <code>/addlemon &lt;amount&gt;</code> – like <code>/addlemon 50</code>. Easy, right? 🙄", parse_mode='HTML')
        return
    amount = int(args[0])
    user_lemons[user_id] = user_lemons[user_id] + amount
    new_lemons = user_lemons[user_id]
    await update.message.reply_text(get_random_message("added_gold", amount=amount, new_gold=new_lemons), parse_mode='HTML')

async def remove_lemons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    if user_id not in user_lemons:
        await update.message.reply_text(get_random_message("no_gold_start"), parse_mode='HTML')
        return
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("📢 Usage: <code>/removelemon &lt;amount&gt;</code> – e.g., <code>/removelemon 30</code>. Don't mess it up. 😤", parse_mode='HTML')
        return
    amount = int(args[0])
    current = user_lemons[user_id]
    if amount <= current:
        user_lemons[user_id] = current - amount
        new_lemons = user_lemons[user_id]
        await update.message.reply_text(get_random_message("removed_gold", amount=amount, new_gold=new_lemons), parse_mode='HTML')
    else:
        await update.message.reply_text(get_random_message("remove_insufficient", current=current, amount=amount), parse_mode='HTML')

def generate_game_id():
    return "Citrus_" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def newgame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    if user_id in user_game:
        await update.message.reply_text(get_random_message("already_in_match_start"), parse_mode='HTML')
        return
    game_id = generate_game_id()
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={game_id}"

    games[game_id] = {
        "players": [user_id],
        "usernames": {user_id: await get_username(context, user_id)},
        "lemons": {user_id: None},
        "status": "lobby",
        "rounds_history": [],
        "game_starter": user_id
    }
    user_game[user_id] = game_id

    await update.message.reply_text(
        f"🍋 <b>CITRUS SOVEREIGN LOBBY CREATED!</b> 🍋\n\n"
        f"🔗 Share this secret link: {link}\n"
        f"👥 Max 4 players.\n"
        f"⚡ Type <code>/game_start</code> when the crew is ready.\n\n"
        f"<i>May the zingiest win the crown.</i> 👑",
        parse_mode='HTML'
    )

async def game_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    game_id = user_game.get(user_id)
    if not game_id or game_id not in games:
        await update.message.reply_text("You are not in any lobby.")
        return
    game = games[game_id]
    game["timeout_task"] = None

    if user_id != game.get("game_starter"):
        starter_username = game['usernames'].get(game['game_starter'], f"Player{game['game_starter']}")
        await context.bot.send_message(user_id, f"You did not start this game. Please politely ask and/or annoyingly badger {starter_username} to start the game. ", parse_mode='HTML')

        return
    if game["status"] != "lobby":
        await update.message.reply_text(get_random_message("game_already_started"), parse_mode='HTML')
        return
    if len(game["players"]) < 2:
        await update.message.reply_text(get_random_message("need_more_players"), parse_mode='HTML')
        return

    all_char_names = list(CHARACTERS.keys())
    if len(game["players"]) == 2 and "Spy" in all_char_names:
        all_char_names.remove("Spy")
    random.shuffle(all_char_names)

    game["status"] = "active"
    game["current_round"] = 1
    game["total_rounds"] = 5
    game["crowns"] = {}
    game["round_active"] = False
    game["round_bids"] = {}
    game["characters"] = {}

    for pid in game["players"]:
        game["lemons"][pid] = 100
        game["crowns"][pid] = 0
        char_name = all_char_names.pop(0)
        char_data = CHARACTERS[char_name]
        game["characters"][pid] = char_name

        start_bonus = char_data["buff"].get("starting_lemons", 0)
        game["lemons"][pid] += start_bonus

        await context.bot.send_message(pid, f"🍋 Your character: <b>{char_name}</b>.\n<i>{char_data['description']}</i>", parse_mode='HTML')
        
        if char_data["buff"].get("roll_bonus"):
            roll = random.randint(1, 5)
            bonus = roll * 5
            game["lemons"][pid] += bonus
            await context.bot.send_message(pid, f"🎲 {char_name} rolled {roll}! +{bonus} lemons. Total: {game['lemons'][pid]}.")

        if "min_bid" in char_data["debuff"]:
            game.setdefault("min_bid", {})[pid] = char_data["debuff"]["min_bid"]
        if "lose_extra_on_loss" in char_data["debuff"]:
            game.setdefault("lose_extra_on_loss", {})[pid] = char_data["debuff"]["lose_extra_on_loss"]
        if "lose_lemons_on_win" in char_data["debuff"]:
            game.setdefault("lose_lemons_on_win", {})[pid] = char_data["debuff"]["lose_lemons_on_win"]
        if "gap_bn_next" in char_data["debuff"]:
            game.setdefault("gap_bn_next", {})[pid] = char_data["debuff"]["gap_bn_next"]
        if "gap_bn_winner" in char_data["debuff"]:
            game.setdefault("gap_bn_winner", {})[pid] = char_data["debuff"]["gap_bn_winner"]
        if "lose_lemons" in char_data["debuff"]:
            game.setdefault("lose_lemons", {})[pid] = char_data["debuff"]["lose_lemons"]

        if "bonus_crowns_on_high_chest" in char_data["buff"]:
            game.setdefault("bonus_crowns_on_high_chest", {})[pid] = char_data["buff"]["bonus_crowns_on_high_chest"]
            game.setdefault("high_chest_threshold", {})[pid] = char_data["buff"]["high_chest_threshold"]
        if "steal_on_win" in char_data["buff"]:
            game.setdefault("steal_on_win", {})[pid] = char_data["buff"]["steal_on_win"]
        if "gain_vp_on_loss" in char_data["buff"]:
            game.setdefault("gain_vp_on_loss", {})[pid] = char_data["buff"]["gain_vp_on_loss"]
        if "gain_half_on_tie" in char_data["buff"]:
            game.setdefault("gain_half_on_tie", {})[pid] = char_data["buff"]["gain_half_on_tie"]
        if "see_lowest_bid" in char_data["buff"]:
            game.setdefault("see_lowest_bid", {})[pid] = char_data["buff"]["see_lowest_bid"]

    for pid in game["players"]:
        await context.bot.send_message(pid, get_random_message("game_started"), parse_mode='HTML')

    await start_next_round(context, game, game_id)  
                
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.effective_user.id
    game_id = user_game.get(user_id)
    if not game_id or game_id not in games:
        await update.message.reply_text("❌ You're not in any game. Type /newgame to start.", parse_mode='HTML')
        return
    game = games[game_id]
    if game["status"] == "lobby":
        players = [game["usernames"].get(pid, str(pid)) for pid in game["players"]]
        player_str = ", ".join(players)
        await update.message.reply_text(
            get_random_message("status_lobby", game_id=game_id, players=player_str),
            parse_mode='HTML'
        )
    else:
        current_round_display = f"{game['current_round']}/{game['total_rounds']}" if game['current_round'] <= game['total_rounds'] else "Game Over"
        await update.message.reply_text(
            get_random_message("status_active",
                game_id=game_id,
                player_count=len(game['players']),
                round_display=current_round_display,
                gold=game['lemons'][user_id],
                vp=game['crowns'][user_id]
            ),
            parse_mode='HTML'
        )

async def bid_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data
    parts = data.split('|')
    if len(parts) != 3:
        await query.edit_message_text("Invalid bid data.", parse_mode='HTML')
        return
    _, game_id, bid_str = parts
    bid = int(bid_str)
    game = games.get(game_id)

    if not game:
        await query.edit_message_text("Game not found.", parse_mode='HTML')
        return
    
    if not game.get("round_active"):
        await query.edit_message_text("This round has already ended.", parse_mode='HTML')
        return
    if game["status"] != "active":
        await query.edit_message_text("Game is not active.", parse_mode='HTML')
        return
    if user_id not in game["players"]:
        await query.edit_message_text("You are not a player in this game.", parse_mode='HTML')
        return
    if user_id in game["round_bids"]:
        await query.edit_message_text(get_random_message("already_bid"), parse_mode='HTML')
        return
    current_lemons = game["lemons"][user_id]
    min_bid = game.get("min_bid", {}).get(user_id)
    if min_bid and bid < min_bid:
        await query.edit_message_text(f"❌ As a {game['characters'][user_id]}, your minimum bid is {min_bid} lemons.", parse_mode='HTML')
        return
    if bid < 0 or bid > current_lemons:
        await query.edit_message_text(get_random_message("invalid_bid", max_gold=current_lemons), parse_mode='HTML')
        return

    game["round_bids"][user_id] = bid
    bids_count = len(game["round_bids"])
    total = len(game["players"])
    remaining = total - bids_count

    username = game["usernames"][user_id]
    await query.edit_message_text(get_random_message("bid_button_press", bid=bid), parse_mode='HTML')
    status_msg = f"🍋 <b>{username}</b> has bid. \n\n<b>Bids</b>: {bids_count}/{total}. \n<i>{remaining} more player(s) left to bid.</i>"

    for pid in game["players"]:
        await context.bot.send_message(pid, status_msg, parse_mode="HTML")
    
    bids = game["round_bids"]
    sorted_bids = sorted(bids.items(), key=lambda x: x[1], reverse=False)
    lowest_bid = sorted_bids[0][1] if sorted_bids else 0

    if len(game["round_bids"]) >= 1:
        lowest_bid = min(game["round_bids"].values())
        for pid in game["players"]:
            if game.get("see_lowest_bid", {}).get(pid) and pid not in game["round_bids"]:
                await context.bot.send_message(pid, f"As a spy, you have managed to gain espionage information about the lowest bid. So far, the lowest bid is {lowest_bid}", parse_mode='HTML')

    if bids_count == total:
        await resolve_round(context, game, game_id)
   
async def resolve_round(context, game, game_id):
    # Guard: prevent double resolution
    if not game.get("round_active"):
        return
    # Immediately mark as resolved to block any further calls
    game["round_active"] = False

    bids = game["round_bids"]
    sorted_desc = sorted(bids.items(), key=lambda x: x[1], reverse=True)
    highest_bid = sorted_desc[0][1] if sorted_desc else 0
    winner_id = None
    tied_winners = []

    if len(sorted_desc) > 1 and sorted_desc[1][1] == highest_bid:
        winner_id = None
        tied_winners = [pid for pid, b in sorted_desc if b == highest_bid]
    else:
        winner_id = sorted_desc[0][0]

    losers = [pid for pid in game["players"] if bids.get(pid, 0) < highest_bid]

    for pid, bid in bids.items():
        game["lemons"][pid] -= bid

    lose_extra = game.get("lose_extra_on_loss", {})
    for pid in losers:
        extra = lose_extra.get(pid, 0)
        if extra:
            game["lemons"][pid] = max(0, game["lemons"][pid] - extra)
            await context.bot.send_message(pid, f"As a {game['characters'][pid]}, you lost an additional {extra} lemons.")

    lose_lemons_on_win = game.get("lose_lemons_on_win", {})
    if winner_id:
        penalty = lose_lemons_on_win.get(winner_id, 0)
        if penalty:
            game["lemons"][winner_id] = max(0, game["lemons"][winner_id] - penalty)
            await context.bot.send_message(winner_id, f"As a {game['characters'][winner_id]}, you lost {penalty} lemons despite winning.")

    steal_on_win = game.get("steal_on_win", {})
    if winner_id and steal_on_win.get(winner_id):
        steal_amount = steal_on_win[winner_id]
        others = [p for p in game["players"] if p != winner_id]
        if others:
            max_lemons = max(game["lemons"][p] for p in others)
            richest = [p for p in others if game["lemons"][p] == max_lemons]
            target = random.choice(richest)
            to_steal = min(steal_amount, game["lemons"][target])
            if to_steal > 0:
                game["lemons"][target] -= to_steal
                game["lemons"][winner_id] += to_steal
                await context.bot.send_message(winner_id, f"You stole {to_steal} lemons from {game['usernames'][target]}.")
                await context.bot.send_message(target, f"{game['usernames'][winner_id]} (Usurper) stole {to_steal} lemons from you.")

    bonus_crowns = game.get("bonus_crowns_on_high_chest", {})
    high_threshold = game.get("high_chest_threshold", {})
    if winner_id and bonus_crowns.get(winner_id):
        chest_val = game['current_chest']
        if chest_val >= high_threshold.get(winner_id, 40):
            game["crowns"][winner_id] += bonus_crowns[winner_id]
            await context.bot.send_message(winner_id, f"Noble: you gained {bonus_crowns[winner_id]} bonus crowns for a high chest ({chest_val}).")

    gain_vp_on_loss = game.get("gain_vp_on_loss", {})
    if winner_id:
        for pid in losers:
            vp_gain = gain_vp_on_loss.get(pid, 0)
            if vp_gain:
                game["crowns"][pid] += vp_gain
                await context.bot.send_message(pid, f"Cultist: you gained {vp_gain} crowns for losing.")

    gain_half_on_tie = game.get("gain_half_on_tie", {})
    if winner_id is None and tied_winners:
        for pid in tied_winners:
            if gain_half_on_tie.get(pid):
                half = game['current_chest'] // 2
                game["crowns"][pid] += half
                await context.bot.send_message(pid, f"Broker: you gained half the chest ({half} crowns) from the tie.")

    gap_bn_next = game.get("gap_bn_next", {})
    lose_lemons = game.get("lose_lemons", {})
    sorted_asc = sorted(bids.items(), key=lambda x: x[1])
    for i, (pid, bid) in enumerate(sorted_asc):
        gap = gap_bn_next.get(pid)
        if gap:
            if i == 0:
                closest = sorted_asc[1][1] if len(sorted_asc) > 1 else bid
            elif i == len(sorted_asc) - 1:
                closest = sorted_asc[-2][1]
            else:
                closest = min(abs(bid - sorted_asc[i-1][1]), abs(bid - sorted_asc[i+1][1]))
            diff = abs(bid - closest)
            if diff > gap:
                lose = lose_lemons.get(pid, 5)
                game["lemons"][pid] = max(0, game["lemons"][pid] - lose)
                await context.bot.send_message(pid, f"Broker debuff: you were too far from the pack, lost {lose} lemons.")

    gap_bn_winner = game.get("gap_bn_winner", {})
    for pid in losers: 
        gap = gap_bn_winner.get(pid)
        if gap:
            diff = highest_bid - bids[pid]
            if diff > gap:
                lose = lose_lemons.get(pid, 5)
                game["lemons"][pid] = max(0, game["lemons"][pid] - lose)
                await context.bot.send_message(pid, f"Spy debuff: you were too far from the highest bid, lost {lose} lemons.")

    crowns_awarded = 0
    if winner_id:
        chest = game['current_chest']
        game['crowns'][winner_id] += chest
        crowns_awarded = chest

    result = f"📢 <b>Round {game['current_round']} Results</b> 📢\n"
    if winner_id:
        winner_name = game['usernames'].get(winner_id, f"Player{winner_id}")
        result += get_random_message("round_result_win", highest_bid=highest_bid, vp=crowns_awarded, winner=winner_name)
    else:
        result += get_random_message("round_result_tie", highest_bid=highest_bid)
    result += "\n🍋 Lemons deducted from all players.\n📊 Type <code>/status</code> to check your remaining lemons and crowns."

    round_record = {
        "round": game["current_round"],
        "chest": game["current_chest"],
        "bids": {pid: bids[pid] for pid in game["players"]},
        "winner_id": winner_id,
        "crowns_awarded": crowns_awarded
    }
    game["rounds_history"].append(round_record)

    for pid in game["players"]:
        personal = result + f"\n\n✨ <b>Your lemons:</b> {game['lemons'][pid]} | <b>Your crowns:</b> {game['crowns'][pid]}"
        await context.bot.send_message(pid, personal, parse_mode='HTML')

    game["current_round"] += 1

    if game.get("timeout_task"):
        game["timeout_task"].cancel()
        game["timeout_task"] = None

    await start_next_round(context, game, game_id)

async def start_next_round(context, game, game_id):
    if game["current_round"] > game["total_rounds"]:
        await end_game(context, game, game_id)
        return

    chest_crowns = random.randint(10, 60)
    game["current_chest"] = chest_crowns
    game["round_active"] = True
    game["round_bids"] = {}

    for pid in game["players"]:
        max_lemons = game["lemons"][pid]
        step = 5
        amounts = list(range(0, max_lemons + 1, step))
        if max_lemons % step != 0:
            amounts.append(max_lemons)
        amounts = sorted(set(amounts))
        min_bid = game.get("min_bid", {}).get(pid, 0)
        amounts = [a for a in amounts if a >= min_bid]
        buttons = []
        row = []
        for amt in amounts:
            callback_data = f"bid|{game_id}|{amt}"
            row.append(InlineKeyboardButton(str(amt), callback_data=callback_data))
            if len(row) == 4:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        if max_lemons not in amounts:
            buttons.append([InlineKeyboardButton(f"MAX ({max_lemons})", callback_data=f"bid|{game_id}|{max_lemons}")])
        reply_markup = InlineKeyboardMarkup(buttons)

        await context.bot.send_message(
            pid,
            get_random_message("round_start",
                round_num=game['current_round'],
                chest=chest_crowns,
                max_bid=max_lemons
            ),
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        if game.get("timeout_task"):
            game["timeout_task"].cancel()
            game["timeout_task"] = None

        game["timeout_task"] = asyncio.create_task(bid_timeout(context, game_id, 60))

async def bid_timeout(context, game_id, seconds):
    await asyncio.sleep(seconds)
    game = games.get(game_id)

    if not game or not game.get("round_active"):
        return

    if len(game["round_bids"]) == len(game["players"]):
        return

    for pid in game["players"]:
        if pid not in game["round_bids"]:
            game["round_bids"][pid] = 0
            msg = "⏰ Time's up! You have been auto‑bid 0 lemons. All bids are now final."
        else:
            msg = "⏰ 60 seconds have passed. All bids are now final."

        await context.bot.send_message(pid, msg, parse_mode='HTML')

    game["timeout_task"] = None

    if len(game["round_bids"]) == len(game["players"]):
        await resolve_round(context, game, game_id)

async def end_game(context, game, game_id):
    best_crowns = max(game["crowns"].values())
    winners = [pid for pid, crowns in game["crowns"].items() if crowns == best_crowns]
   
    if len(winners) == 1:
        final_msg = get_random_message("game_over_win",
            winner=game['usernames'].get(winners[0], f"Player{winners[0]}"),
            vp=best_crowns
        )
    else:
        winner_names = ", ".join(game['usernames'].get(pid, f"Player{pid}") for pid in winners)
        final_msg = get_random_message("game_over_tie",
            winners=winner_names,
            vp=best_crowns
        )

    character_assignments = ""
    character_assignments += "<b>🎭 Character Assignments:</b> \n"
    for pid in game["players"]:
        username = game['usernames'].get(pid, f"Player{pid}")
        character = game['characters'][pid]
        description = CHARACTERS[character]["description"]
        character_assignments += f"<b>{username}</b>: <code>{character}</code> <i>({description})</i>\n"
      
    summary = ""
    summary += character_assignments

    for rec in game["rounds_history"]:
        summary += f"<b>Round {rec['round']}</b>\n"
        summary += f"👑 Crowns in chest: {rec['chest']}\n"
        for pid, bid in rec["bids"].items():
            uname = game['usernames'].get(pid, f"Player{pid}")
            summary += f"   {uname} bid {bid} lemons\n"
        if rec["winner_id"]:
            winner_name = game['usernames'].get(rec["winner_id"], f"Player{rec['winner_id']}")
            summary += f"🏅 Winner: {winner_name} (gains {rec['crowns_awarded']} crowns)\n"
        else:
            summary += f"🏅 Winner: Tie – no crowns awarded\n"
        summary += "\n"

    summary += "<b>🍋 FINAL CROWN COUNT</b> 👑\n"
    for pid in game["players"]:
        summary += f"   {game['usernames'].get(pid, f'Player{pid}')}: {game['crowns'][pid]} crowns\n"
    summary += f"\n{final_msg}"

    final_text = get_random_message("final_summary", summary=summary)

    keyboard = [
        [InlineKeyboardButton("🔄 Restart Game", callback_data=f"restart|{game_id}")],
        [InlineKeyboardButton("❌ End Game", callback_data=f"delete|{game_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    for pid in game["players"]:
        await context.bot.send_message(pid, final_text, parse_mode='HTML', reply_markup=reply_markup)

    game["ended"] = True
    game["cleanup_task"] = asyncio.create_task(cleanup_game(context, game_id))

async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    _, game_id = data.split('|')
    game = games.get(game_id)
    
    if not game:
        await query.edit_message_text("Game already ended.")
        return
    
    if game.get("cleanup_task"):
        game["cleanup_task"].cancel()

    for pid in game["players"]:
        await context.bot.send_message(pid, "🏁 The game has been ended by a player. Thanks for playing!", parse_mode='HTML')
        if pid in user_game:
            del user_game[pid]

    del games[game_id]

    await query.edit_message_text("✅ Game deleted successfully.")

async def cleanup_game(context, game_id):
    await asyncio.sleep(300)
    game = games.get(game_id)
    if not game:
        return
    if not game.get("ended"):
        return
    for pid in game["players"]:
        await context.bot.send_message(pid, "🕐 Restart window expired. Game has been archived.", parse_mode='HTML')
        if pid in user_game:
            del user_game[pid]
    del games[game_id]

async def restart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    _, game_id = data.split('|')
    game = games.get(game_id)
    if not game:
        await query.edit_message_text("Game no longer exists.")
        return
    if not game.get("ended"):
        await query.edit_message_text("Game is still active.")
        return

    if game.get("cleanup_task"):
        game["cleanup_task"].cancel()
        game["cleanup_task"] = None
    
    game["ended"] = False
    game["current_round"] = 1
    game["total_rounds"] = 5
    game["crowns"] = {pid: 0 for pid in game["players"]}
    game["round_active"] = False
    game["round_bids"] = {}
    game["rounds_history"] = []
    game["timeout_task"] = None

    for pid in game["players"]:
        char_name = game["characters"][pid]
        char_data = CHARACTERS[char_name]
        game["lemons"][pid] = 100 + char_data["buff"].get("starting_lemons", 0)
        if char_data["buff"].get("roll_bonus"):
            roll = random.randint(1, 5)
            bonus = roll * 5
            game["lemons"][pid] += bonus
            await context.bot.send_message(pid, f"🎲 {char_name} re‑rolled {roll}! +{bonus} lemons. Total: {game['lemons'][pid]}.")

    await start_next_round(context, game, game_id)
    
    await query.edit_message_text("✅ Game restarted! Check your DMs for the new round.")

async def leave_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    game_id = user_game.get(user_id)
    if not game_id or game_id not in games:
        await update.message.reply_text("You are not part of any citrus kingdoms at the moment. Maybe join one before you try to leave, m'kay?")
        return
    
    game = games[game_id]
    status = game["status"]

    game["players"].remove(user_id)
    del game["usernames"][user_id]
    del game["lemons"][user_id]
    if "crowns" in game:
        del game["crowns"][user_id]
    if "characters" in game: del game["characters"][user_id]
    for dict_key in ["min_bid", "lose_extra_on_loss", "lose_lemons_on_win",
                     "bonus_crowns_on_high_chest", "high_chest_threshold",
                     "steal_on_win", "gain_vp_on_loss"]:
        if dict_key in game and user_id in game[dict_key]:
            del game[dict_key][user_id]

    del user_game[user_id]

    if status == "lobby":
        await update.message.reply_text("You have successfully ran away before the game even started. Congratulations.")
        if len(game["players"]) == 0:
            del games[game_id]
            await update.message.reply_text("🔥Burning the citrus kingdom to the ground. Everyone left. I can't stand the emptiness")
            return
        else:
            remaining_ids = game["players"]
            remaining_players = [game["usernames"][pid] for pid in remaining_ids]
            message = f"❌ {await get_username(context, user_id)} has cowwardly run. Such a sourpuff.😒\n Here are the remaining players: {', '.join(remaining_players)}"
            for pid in remaining_ids:
                await context.bot.send_message(pid, message, parse_mode='HTML')
    
    if status == "active":
        await update.message.reply_text("You have successfully ran away before the game ended. Too scared to face the possibility of a loss? Pathetic😒")
        if game.get("round_active") and user_id in game["round_bids"]:
            del game["round_bids"][user_id]

        remaining_count = len(game["players"])

        if remaining_count < 2:
            if remaining_count == 1:
                winner_id = game["players"][0]
                await end_game(context, game, game_id)
                return
            else:
                del games[game_id]
                await update.message.reply_text("Citrus Empire abandoned. Not enough players")
                return
        else:
            remaining_names = [game["usernames"][pid] for pid in game["players"]]
            message = f"❌ {await get_username(context, user_id)} has cowwardly run. Such a sourpuff😒. I guess that means increased odds for you to win...\n Continuing the game with: {', '.join(remaining_names)}"
            for pid in game["players"]:
                await context.bot.send_message(pid, message, parse_mode='HTML')

        if game.get("round_active"):
            if len(game["round_bids"]) == len(game["players"]):
                await resolve_round(context, game, game_id)
            else:
                bids_count = len(game["round_bids"])
                total = len(game["players"])
                remaining_to_bid = total - bids_count
                status_msg = f"🔄 After player left: {bids_count}/{total} bids received. {remaining_to_bid} player(s) still need to bid."
                for pid in game["players"]:
                        await context.bot.send_message(pid, status_msg, parse_mode='HTML')

async def stop_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    game_id = user_game.get(user_id)

    if not game_id or game_id not in games:
        await update.message.reply_text("You are not part of any citrus kingdoms at the moment. Maybe join one before you try to leave, m'kay?")
        return
    
    game = games[game_id]

    if user_id != game.get("game_starter"):
        starter_username = game['usernames'].get(game['game_starter'], f"Player{game['game_starter']}")
        await update.message.reply_text(f"Only the game creator ({starter_username}) can stop the game. Ask them politely, or bribe them with lemons.")
        return
    
    status = game["status"]

    if status == "lobby":
        for pid in game["players"]:
            if pid != user_id:
                await context.bot.send_message(pid, "🍋 The host has cancelled the lobby. The game has been dissolved. No crowns for anyone today.")
            await update.message.reply_text("You have successfully dissolved the lobby. The citrus kingdom has been abandoned.")

        for pid in game["players"]:
            if pid in user_game:
                del user_game[pid]
        del games[game_id]

    elif status == "active":
        for pid in game["players"]:
            await context.bot.send_message(pid, "⛔ The host has stopped the game early! Calculating final standings based on current crowns...")
        await end_game(context, game, game_id)

    else:
        await update.message.reply_text("Game is in an unknown state. Cannot stop.")
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    
    first_page = HELP_ORDER[0]
    page_data = HELP_PAGES[first_page]

    keyboard = [
        [InlineKeyboardButton("➡️ Next", callback_data=f"help_next|{first_page}")],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ]

    await update.message.reply_text(
        f"<b>{page_data['title']}</b>\n\n{page_data['text']}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "help_close":
        await query.edit_message_text("👋 Help closed. Good luck, future Sovereign!")
        return
    
    action, current_key = data.split('|')

    try:
        idx = HELP_ORDER.index(current_key)
    except:
        idx = 0

    if action == "help_next":
        new_idx = (idx+1) % len(HELP_ORDER)
    else:
        new_idx = (idx-1) % len(HELP_ORDER)

    new_key = HELP_ORDER[new_idx]
    page_data = HELP_PAGES[new_key]

    keyboard = []
    if len(HELP_ORDER) > 1:
        row = []
        if new_idx > 0:
            row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"help_prev|{new_key}"))
        if new_idx < len(HELP_ORDER) - 1:
            row.append(InlineKeyboardButton("➡️ Next", callback_data=f"help_next|{new_key}"))
        if row:
            keyboard.append(row)
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="help_close")])
    
    await query.edit_message_text(
        f"<b>{page_data['title']}</b>\n\n{page_data['text']}",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    await update.message.reply_text(
        "<b>🍋 Citrus Sovereign</b>\n"
        "<i>A bidding game of lemon‑powered treachery.</i>\n\n"
        "First game project – currently in open beta by <b>@bearly_learning</b>.\n\n"
        "Made with love, support and help from:\n"
        "<b>@bluelightreverie</b>\n"
        "<b>@cerebralsymphony</b>\n"
        "<b>@I_Build_stuff</b>\n"
        "<b>@thechillcodinglounge</b> and \n"
        "<b>All the DIC members</b>\n\n"
        "<i>세상에서 가장 달콤한 레몬에게 ❤️^^ .</i>",
        parse_mode='HTML'
    )

def main():
    web_thread = threading.Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()


    TOKEN = os.environ.get("BOT_TOKEN", "8826395440:AAHt97Os184a6bg95GcxPUIZdQP42_CVACE")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("lemons", lemons_command))
    application.add_handler(CommandHandler("addlemon", add_lemons_command))
    application.add_handler(CommandHandler("removelemon", remove_lemons_command))
    application.add_handler(CommandHandler("newgame", newgame_command))
    application.add_handler(CommandHandler("game_start", game_start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("leave", leave_command))
    application.add_handler(CallbackQueryHandler(bid_button_callback, pattern="^bid\\|"))
    application.add_handler(CallbackQueryHandler(restart_callback, pattern="^restart\\|"))
    application.add_handler(CommandHandler("stopgame", stop_game_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(help_callback, pattern="^help_"))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CallbackQueryHandler(delete_callback, pattern="^delete\\|"))

    try:
        asyncio.get_running_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    application.run_polling()
if __name__ == "__main__":
    main()