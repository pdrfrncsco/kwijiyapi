"""
Seed data command — populates the database with:
- Kimbundu language
- Words (50+ vocabulary items across 3 levels)
- Questions (30+ questions across 3 levels)
- Badges
"""

from django.core.management.base import BaseCommand
from languages.models import Language
from quizzes.models import Word, Question, Option
from gamification.models import Badge


class Command(BaseCommand):
    help = 'Seed the database with Kimbundu language data for the MVP'

    def handle(self, *args, **options):
        self.stdout.write('🌍 Seeding Kwijiya database...\n')

        # 1. Create Language
        language, created = Language.objects.get_or_create(
            code='kmb',
            defaults={
                'name': 'Kimbundu',
                'description': (
                    'Kimbundu é uma língua bantu falada principalmente nas províncias '
                    'de Luanda, Malanje, Bengo e Kwanza Norte. É uma das línguas '
                    'nacionais mais faladas de Angola.'
                ),
                'region': 'Luanda, Malanje, Bengo, Kwanza Norte',
                'difficulty_level': 'medium',
                'num_speakers': '~3 milhões',
                'is_active': True,
            }
        )
        self.stdout.write(f'  {"✅ Criada" if created else "⏩ Existente"}: {language}\n')

        # Also create future languages (inactive)
        future_languages = [
            ('Umbundu', 'umb', 'Huambo, Bié, Benguela', '~6 milhões'),
            ('Kikongo', 'kik', 'Zaire, Uíge, Cabinda', '~2 milhões'),
            ('Cokwe', 'cjk', 'Lunda Norte, Lunda Sul, Moxico', '~1 milhão'),
            ('Ngangela', 'nba', 'Moxico, Cuando Cubango', '~500 mil'),
        ]
        for name, code, region, speakers in future_languages:
            lang, created = Language.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'region': region,
                    'num_speakers': speakers,
                    'is_active': False,  # Not available yet
                }
            )
            if created:
                self.stdout.write(f'  ➕ Futura: {lang}\n')

        # 2. Create Words
        self.stdout.write('\n📚 Seeding words...\n')
        words_data = [
            # Level 1 — Saudações e Pronomes
            ('Eme', 'Eu', 1, 'pronomes', 'Pronome pessoal da primeira pessoa do singular.'),
            ('Eye', 'Tu', 1, 'pronomes', 'Pronome pessoal da segunda pessoa do singular.'),
            ('Ene', 'Ele/Ela', 1, 'pronomes', 'Pronome pessoal da terceira pessoa do singular.'),
            ('Etu', 'Nós', 1, 'pronomes', 'Pronome pessoal da primeira pessoa do plural.'),
            ('Enu', 'Vós/Vocês', 1, 'pronomes', 'Pronome pessoal da segunda pessoa do plural.'),
            ('Ala', 'Eles/Elas', 1, 'pronomes', 'Pronome pessoal da terceira pessoa do plural.'),
            ('Kiambote', 'Olá/Bom dia', 1, 'saudacoes', 'Saudação formal em Kimbundu. Usada para cumprimentar.'),
            ('Kala kiambote', 'Fique bem', 1, 'saudacoes', 'Despedida formal em Kimbundu.'),
            ('Weza kiambote', 'Bem-vindo', 1, 'saudacoes', 'Expressão de boas-vindas.'),
            ('Inga', 'Sim', 1, 'saudacoes', 'Afirmação en Kimbundu.'),
            ('Kana', 'Não', 1, 'saudacoes', 'Negação em Kimbundu.'),
            ('Ngibanze', 'Obrigado', 1, 'saudacoes', 'Expressão de gratidão.'),
            ('Tata', 'Pai', 1, 'familia', 'Pai na tradição Kimbundu.'),
            ('Mama', 'Mãe', 1, 'familia', 'Mãe na tradição Kimbundu.'),
            ('Mona', 'Filho/Criança', 1, 'familia', 'Criança ou filho em Kimbundu.'),
            ('Dikota', 'Mais velho/Ancião', 1, 'familia', 'Termo de respeito para pessoas mais velhas.'),
            # Level 2 — Verbos e Números
            ('Kudya', 'Comer', 2, 'verbos', 'Verbo comer no infinitivo.'),
            ('Kunwa', 'Beber', 2, 'verbos', 'Verbo beber no infinitivo.'),
            ('Kwenda', 'Ir/Andar', 2, 'verbos', 'Verbo ir ou andar no infinitivo.'),
            ('Kubanga', 'Fazer', 2, 'verbos', 'Verbo fazer no infinitivo.'),
            ('Kumona', 'Ver', 2, 'verbos', 'Verbo ver no infinitivo.'),
            ('Kuzuela', 'Falar', 2, 'verbos', 'Verbo falar no infinitivo.'),
            ('Kutena', 'Amar', 2, 'verbos', 'Verbo amar no infinitivo.'),
            ('Kukala', 'Estar/Ser', 2, 'verbos', 'Verbo ser ou estar no infinitivo.'),
            ('Mosi', 'Um', 2, 'numeros', 'Número um.'),
            ('Iari', 'Dois', 2, 'numeros', 'Número dois.'),
            ('Tatu', 'Três', 2, 'numeros', 'Número três.'),
            ('Uana', 'Quatro', 2, 'numeros', 'Número quatro.'),
            ('Tanu', 'Cinco', 2, 'numeros', 'Número cinco.'),
            ('Samanu', 'Seis', 2, 'numeros', 'Número seis.'),
            ('Sambari', 'Sete', 2, 'numeros', 'Número sete.'),
            ('Nake', 'Oito', 2, 'numeros', 'Número oito.'),
            # Level 3 — Cultura, Natureza, Frases
            ('Nzambi', 'Deus', 3, 'cultura', 'Deus na tradição espiritual Kimbundu.'),
            ('Kijila', 'Proibição/Tabu', 3, 'cultura', 'Restrição cultural ou espiritual.'),
            ('Kilombo', 'Acampamento/Comunidade', 3, 'cultura', 'Origem da palavra "quilombo" no Brasil.'),
            ('Sanzala', 'Aldeia', 3, 'cultura', 'Comunidade rural tradicional.'),
            ('Mbanza', 'Cidade/Capital', 3, 'cultura', 'Cidade ou capital. Origem de "Mbanza Kongo".'),
            ('Nzoji', 'Sonho', 3, 'natureza', 'Sonho na tradição Kimbundu.'),
            ('Ndandu', 'Crocodilo', 3, 'animais', 'Animal respeitado na cultura angolana.'),
            ('Ngulu', 'Porco', 3, 'animais', 'Porco em Kimbundu.'),
            ('Njila', 'Caminho', 3, 'natureza', 'Caminho. Também nome de divindade nas tradições.'),
            ('Kalunga', 'Mar/Oceano', 3, 'natureza', 'Mar ou oceano. Símbolo espiritual importante.'),
            ('Mutue', 'Cabeça', 3, 'corpo', 'Cabeça no corpo humano.'),
            ('Muxima', 'Coração', 3, 'cultura', 'Coração. Também nome da famosa igreja de Muxima.'),
        ]

        words = {}
        for native, portuguese, diff, cat, explanation in words_data:
            word, created = Word.objects.get_or_create(
                language=language,
                word_native=native,
                defaults={
                    'word_portuguese': portuguese,
                    'difficulty': diff,
                    'category': cat,
                    'explanation': explanation,
                }
            )
            words[native] = word
            if created:
                self.stdout.write(f'  ✅ {native} → {portuguese}\n')

        # 3. Create Questions
        self.stdout.write('\n❓ Seeding questions...\n')
        questions_data = [
            # Level 1 — Translation questions
            {
                'text': 'Como se diz "Eu" em Kimbundu?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Eme" é o pronome pessoal da primeira pessoa do singular em Kimbundu.',
                'cultural': 'Na tradição oral Kimbundu, o uso do pronome reforça a identidade individual.',
                'options': [('Eme', True), ('Eye', False), ('Etu', False), ('Ene', False)],
                'word': 'Eme',
            },
            {
                'text': 'Qual é a tradução de "Kiambote"?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Kiambote" é a saudação formal em Kimbundu, equivalente a "Olá" ou "Bom dia".',
                'cultural': 'Em Angola, cumprimentar é um acto cultural profundo de respeito.',
                'options': [('Olá/Bom dia', True), ('Adeus', False), ('Obrigado', False), ('Desculpe', False)],
                'word': 'Kiambote',
            },
            {
                'text': 'Como se diz "Obrigado" em Kimbundu?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Ngibanze" expressa gratidão em Kimbundu.',
                'cultural': 'A gratidão é um pilar fundamental nas relações comunitárias angolanas.',
                'options': [('Ngibanze', True), ('Kiambote', False), ('Kana', False), ('Inga', False)],
                'word': 'Ngibanze',
            },
            {
                'text': 'O que significa "Mona" em português?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Mona" significa filho ou criança em Kimbundu.',
                'cultural': 'Na cultura Kimbundu, as crianças são consideradas bênção da comunidade.',
                'options': [('Filho/Criança', True), ('Pai', False), ('Mãe', False), ('Avó', False)],
                'word': 'Mona',
            },
            {
                'text': 'Qual é o pronome para "Nós" em Kimbundu?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Etu" é o pronome da primeira pessoa do plural.',
                'cultural': 'O sentido coletivo é muito forte na cultura Kimbundu.',
                'options': [('Etu', True), ('Eme', False), ('Eye', False), ('Ala', False)],
                'word': 'Etu',
            },
            {
                'text': 'Como se diz "Sim" em Kimbundu?',
                'type': 'multiple_choice', 'diff': 1, 'xp': 100,
                'explanation': '"Inga" é a forma afirmativa em Kimbundu.',
                'cultural': '',
                'options': [('Inga', True), ('Kana', False), ('Eye', False), ('Ene', False)],
                'word': 'Inga',
            },
            {
                'text': 'O que significa "Kana"?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Kana" é a negação em Kimbundu, equivalente a "Não".',
                'cultural': '',
                'options': [('Não', True), ('Sim', False), ('Talvez', False), ('Sempre', False)],
                'word': 'Kana',
            },
            {
                'text': 'Como se diz "Fique bem" em Kimbundu?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Kala kiambote" é uma despedida formal.',
                'cultural': 'A despedida em Kimbundu carrega um desejo genuíno de bem-estar.',
                'options': [('Kala kiambote', True), ('Kiambote', False), ('Weza kiambote', False), ('Ngibanze', False)],
                'word': 'Kala kiambote',
            },
            {
                'text': 'O que significa "Tata" em Kimbundu?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Tata" significa pai em Kimbundu.',
                'cultural': 'O pai na cultura Kimbundu é o pilar da família e da tradição.',
                'options': [('Pai', True), ('Mãe', False), ('Filho', False), ('Irmão', False)],
                'word': 'Tata',
            },
            {
                'text': 'Qual é a tradução de "Dikota"?',
                'type': 'translation', 'diff': 1, 'xp': 100,
                'explanation': '"Dikota" refere-se a uma pessoa mais velha ou ancião.',
                'cultural': 'Os dikota são respeitados como guardiões da sabedoria e tradição.',
                'options': [('Mais velho/Ancião', True), ('Jovem', False), ('Criança', False), ('Bebé', False)],
                'word': 'Dikota',
            },

            # Level 2 — Verbs and Numbers
            {
                'text': 'Como se diz "Comer" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Kudya" é o verbo comer no infinitivo em Kimbundu.',
                'cultural': 'A partilha de refeições é um acto comunitário sagrado na cultura angolana.',
                'options': [('Kudya', True), ('Kunwa', False), ('Kwenda', False), ('Kubanga', False)],
                'word': 'Kudya',
            },
            {
                'text': 'Qual é o verbo "Falar" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Kuzuela" é o verbo falar em Kimbundu.',
                'cultural': 'A tradição oral é a principal forma de transmissão cultural em Kimbundu.',
                'options': [('Kuzuela', True), ('Kumona', False), ('Kutena', False), ('Kukala', False)],
                'word': 'Kuzuela',
            },
            {
                'text': 'O que significa "Kwenda"?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Kwenda" significa ir ou andar.',
                'cultural': '',
                'options': [('Ir/Andar', True), ('Comer', False), ('Dormir', False), ('Beber', False)],
                'word': 'Kwenda',
            },
            {
                'text': 'Como se diz "Amar" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Kutena" é o verbo amar em Kimbundu.',
                'cultural': 'O amor em Kimbundu está ligado ao conceito de comunidade e pertença.',
                'options': [('Kutena', True), ('Kuzuela', False), ('Kudya', False), ('Kukala', False)],
                'word': 'Kutena',
            },
            {
                'text': 'Qual é o número "Três" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Tatu" é o número três em Kimbundu.',
                'cultural': 'O número três tem significado especial em muitas tradições bantu.',
                'options': [('Tatu', True), ('Iari', False), ('Uana', False), ('Tanu', False)],
                'word': 'Tatu',
            },
            {
                'text': 'Como se diz "Cinco" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Tanu" é o número cinco em Kimbundu.',
                'cultural': 'Os números em Kimbundu seguem o sistema de contagem bantu.',
                'options': [('Tanu', True), ('Samanu', False), ('Tatu', False), ('Mosi', False)],
                'word': 'Tanu',
            },
            {
                'text': 'O que significa "Kukala"?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Kukala" é o verbo ser/estar em Kimbundu.',
                'cultural': '',
                'options': [('Estar/Ser', True), ('Fazer', False), ('Ver', False), ('Falar', False)],
                'word': 'Kukala',
            },
            {
                'text': 'Como se diz "Um" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Mosi" é o número um em Kimbundu.',
                'cultural': '',
                'options': [('Mosi', True), ('Iari', False), ('Tatu', False), ('Uana', False)],
                'word': 'Mosi',
            },
            {
                'text': 'Qual verbo significa "Ver" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Kumona" é o verbo ver em Kimbundu.',
                'cultural': '',
                'options': [('Kumona', True), ('Kuzuela', False), ('Kunwa', False), ('Kwenda', False)],
                'word': 'Kumona',
            },
            {
                'text': 'O que significa "Samanu" em Kimbundu?',
                'type': 'translation', 'diff': 2, 'xp': 150,
                'explanation': '"Samanu" é o número seis em Kimbundu.',
                'cultural': '',
                'options': [('Seis', True), ('Sete', False), ('Cinco', False), ('Oito', False)],
                'word': 'Samanu',
            },

            # Level 3 — Culture, Nature, Complex
            {
                'text': 'O que significa "Kilombo" em Kimbundu?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Kilombo" significa acampamento ou comunidade em Kimbundu.',
                'cultural': 'A palavra "quilombo" usada no Brasil tem origem no Kimbundu "kilombo". '
                            'Refere-se às comunidades de resistência criadas por africanos escravizados.',
                'options': [('Acampamento/Comunidade', True), ('Cidade', False), ('Floresta', False), ('Rio', False)],
                'word': 'Kilombo',
            },
            {
                'text': 'Qual é o significado de "Muxima"?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Muxima" significa coração em Kimbundu.',
                'cultural': 'Muxima é também o nome da famosa igreja de Nossa Senhora da Muxima, '
                            'um dos maiores centros de peregrinação em Angola.',
                'options': [('Coração', True), ('Alma', False), ('Mente', False), ('Espírito', False)],
                'word': 'Muxima',
            },
            {
                'text': 'O que representa "Kalunga" na cultura Kimbundu?',
                'type': 'multiple_choice', 'diff': 3, 'xp': 200,
                'explanation': '"Kalunga" refere-se ao mar ou oceano.',
                'cultural': 'Kalunga é um conceito espiritual profundo que simboliza a passagem '
                            'entre o mundo dos vivos e dos antepassados.',
                'options': [('Mar/Oceano', True), ('Montanha', False), ('Deserto', False), ('Céu', False)],
                'word': 'Kalunga',
            },
            {
                'text': 'O que significa "Kijila" em Kimbundu?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Kijila" refere-se a uma proibição ou tabu cultural.',
                'cultural': 'As kijila são restrições espirituais que regulam o comportamento '
                            'nas comunidades tradicionais angolanas.',
                'options': [('Proibição/Tabu', True), ('Celebração', False), ('Dança', False), ('Comida', False)],
                'word': 'Kijila',
            },
            {
                'text': 'Qual é o significado de "Mbanza"?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Mbanza" significa cidade ou capital.',
                'cultural': '"Mbanza Kongo" era a capital do antigo Reino do Kongo, '
                            'hoje património mundial da UNESCO.',
                'options': [('Cidade/Capital', True), ('Aldeia', False), ('Mercado', False), ('Templo', False)],
                'word': 'Mbanza',
            },
            {
                'text': 'O que significa "Nzambi" na tradição Kimbundu?',
                'type': 'multiple_choice', 'diff': 3, 'xp': 200,
                'explanation': '"Nzambi" é o nome de Deus na tradição espiritual Kimbundu.',
                'cultural': 'Nzambi (ou Nzambi a Mpungu) é o Ser Supremo nas tradições bantu de Angola.',
                'options': [('Deus', True), ('Rei', False), ('Guerreiro', False), ('Espírito', False)],
                'word': 'Nzambi',
            },
            {
                'text': 'O que significa "Sanzala"?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Sanzala" significa aldeia em Kimbundu.',
                'cultural': 'A palavra "senzala" usada no Brasil tem origem na palavra Kimbundu "sanzala".',
                'options': [('Aldeia', True), ('Cidade', False), ('Palácio', False), ('Mercado', False)],
                'word': 'Sanzala',
            },
            {
                'text': 'Qual é o significado de "Njila"?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Njila" significa caminho em Kimbundu.',
                'cultural': 'Njila é também uma divindade das encruzilhadas nas tradições espirituais angolanas.',
                'options': [('Caminho', True), ('Ponte', False), ('Porta', False), ('Janela', False)],
                'word': 'Njila',
            },
            {
                'text': 'O que significa "Nzoji" em Kimbundu?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Nzoji" significa sonho em Kimbundu.',
                'cultural': 'Nas tradições Kimbundu, os sonhos são considerados mensagens dos antepassados.',
                'options': [('Sonho', True), ('Noite', False), ('Estrela', False), ('Lua', False)],
                'word': 'Nzoji',
            },
            {
                'text': 'Qual animal é "Ndandu" em Kimbundu?',
                'type': 'translation', 'diff': 3, 'xp': 200,
                'explanation': '"Ndandu" é o crocodilo em Kimbundu.',
                'cultural': 'O crocodilo é um animal de grande respeito nas tradições angolanas.',
                'options': [('Crocodilo', True), ('Leão', False), ('Elefante', False), ('Cobra', False)],
                'word': 'Ndandu',
            },
        ]

        for q_data in questions_data:
            word_obj = words.get(q_data.get('word'))
            question, created = Question.objects.get_or_create(
                language=language,
                question_text=q_data['text'],
                defaults={
                    'word': word_obj,
                    'question_type': q_data['type'],
                    'difficulty': q_data['diff'],
                    'explanation': q_data['explanation'],
                    'cultural_note': q_data['cultural'],
                    'timer_seconds': 5 if q_data['diff'] < 3 else 7,
                    'xp_value': q_data['xp'],
                }
            )
            if created:
                for opt_text, is_correct in q_data['options']:
                    Option.objects.create(
                        question=question,
                        text=opt_text,
                        is_correct=is_correct,
                    )
                self.stdout.write(f'  ✅ Q: {q_data["text"][:50]}...\n')

        # 4. Create Badges
        self.stdout.write('\n🏆 Seeding badges...\n')
        badges_data = [
            ('Primeiro Passo', 'Completou o primeiro quiz.', '🎯', 0),
            ('Aprendiz Dedicado', 'Alcançou 500 XP.', '📖', 500),
            ('Estudante Cultural', 'Alcançou 1000 XP.', '🌍', 1000),
            ('Explorador de Línguas', 'Alcançou 2500 XP.', '🗺️', 2500),
            ('Guardião da Tradição', 'Alcançou 5000 XP.', '🛡️', 5000),
            ('Mestre Kimbundu', 'Alcançou 10000 XP.', '👑', 10000),
            ('Streak de Fogo', 'Manteve streak de 7 dias.', '🔥', 0),
            ('Precisão Perfeita', 'Completou quiz com 100% de precisão.', '💎', 0),
        ]

        for name, desc, icon, xp_req in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'icon': icon,
                    'xp_required': xp_req,
                }
            )
            if created:
                self.stdout.write(f'  ✅ {icon} {name}\n')

        # Summary
        self.stdout.write(f'\n🎉 Seed concluído!\n')
        self.stdout.write(f'   Línguas: {Language.objects.count()}\n')
        self.stdout.write(f'   Palavras: {Word.objects.count()}\n')
        self.stdout.write(f'   Perguntas: {Question.objects.count()}\n')
        self.stdout.write(f'   Medalhas: {Badge.objects.count()}\n')
