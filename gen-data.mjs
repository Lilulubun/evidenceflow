// EVIDENCEFLOW PoC — synthetic HR data generator.
// 40 employees x 3 rater roles (self/peer/manager) x 2 quarters (Q3/Q4 2026)
// Every record carries rater/role/quote/timestamp + T' (ingestion time).
// Deterministic via mulberry32(seed) so runs are reproducible.
// No external deps. Node 18+.

function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const rnd = mulberry32(20261014);
const pick = (arr) => arr[Math.floor(rnd()*arr.length)];
const n = (min,max) => Math.floor(rnd()*(max-min+1))+min;

const FIRST = ["Aisha","Bima","Citra","Dewi","Eko","Fajar","Gita","Hadi","Indra","Joko","Kirana","Lukman","Maya","Nadia","Oscar","Putri","Rizky","Sari","Teguh","Umar","Vina","Wahyu","Xena","Yoga","Zahra","Agus","Bella","Candra","Dinda","Eka","Fahmi","Ganis","Herman","Irfan","Jasmine","Kurnia","Lestari","Made","Naufal","Olivia"];
const LAST = ["Pratama","Wibowo","Santoso","Nugraha","Hakim","Siregar","Purnama","Rahman","Wijaya","Kusuma","Saputra","Handayani","Mahendra","Ramadhan","Sulistyo","Anggraini","Prasetyo","Lubis","Hartono","Gunawan"];

const COMPETENCIES = ["communication","delivery_quality","collaboration","initiative","problem_solving","reliability","mentoring","adaptability"];

// Sentiment template pools: quote templates per (sentiment, competency).
const Q = {
  pos: {
    communication: ["explained the {x} incident root-cause clearly to the whole team","led the sprint review and kept questions on track","wrote a crisp postmortem everyone could follow"],
    delivery_quality: ["shipped {x} ahead of deadline with zero regressions","their {x} code needed almost no review comments","handled the migration cleanly"],
    collaboration: ["paired with a junior on {x} for two afternoons","unblocked three other people on {x}","shared a reusable template for {x}"],
    initiative: ["proposed and ran the {x} spike without being asked","volunteered to own the flaky {x} pipeline","drafted the RFC for {x} themselves"],
    problem_solving: ["found the race condition in {x} that had eluded us for weeks","refactored {x} to remove the N+1 queries","isolated the memory leak in {x}"],
    reliability: ["never missed a standup and always had status ready","carried on-call for {x} without escalation once","every {x} estimate landed within 10%"],
    mentoring: ["ran a brownbag on {x} that 12 people attended","rewrote the onboarding doc for {x}","spent Fridays helping juniors debug {x}"],
    adaptability: ["picked up {x} in two weeks when the team lost a member","context-switched to {x} mid-quarter without complaint","learned the new {x} tooling quickly"],
  },
  neg: {
    communication: ["didn't escalate the {x} blocker until the deadline","gave conflicting requirements for {x} in the same week","left {x} decisions out of the doc"],
    delivery_quality: ["{x} was returned by QA twice for the same defect","merged {x} without tests despite the policy","missed the {x} deadline by two weeks"],
    collaboration: ["went silent in the {x} review thread for a week","re-implemented {x} alone instead of pairing","dismissed feedback on {x} in front of juniors"],
    initiative: ["waited for explicit assignment on {x} despite capacity","never picked up the stale {x} ticket","declined to present the {x} findings"],
    problem_solving: ["patched {x} with a workaround instead of fixing the cause","misdiagnosed {x} and cost us a day","kept guessing on {x} instead of reading the logs"],
    reliability: ["missed three standups in a row during {x}","on-call for {x} required two escalations","{x} estimates were off by 3x"],
    mentoring: ["cancelled two scheduled {x} mentoring sessions","left {x} code reviews with no comments","didn't respond to junior questions on {x}"],
    adaptability: ["refused to switch to the new {x} process for a month","blocked {x} migration citing old habits","slow to learn {x} tooling"],
  },
};

const SUBJECTS = ["payment-gateway","reporting service","mobile app","auth migration","k8s rollout","customer dashboard","search indexer","CI pipeline","data pipeline","vendor integration","onboarding flow","billing reconciliation"];

// Personas: archetype drives sentiment distribution.
const PERSONAS = {
  steady:      { pos: 0.65, neg: 0.35 },
  strong:      { pos: 0.85, neg: 0.15 },
  struggling:  { pos: 0.30, neg: 0.70 },
  volatile:    { pos: 0.50, neg: 0.50 }, // varies by quarter below
  improving:   { pos: 0.40, neg: 0.60 }, // flips in Q4
};
const ARCH_KEYS = Object.keys(PERSONAS);

function makeQuote(arch, sentiment, comp, subject){
  const tpl = pick(Q[sentiment][comp]);
  return tpl.replace("{x}", subject);
}

const people = FIRST.map((f,i)=>({
  id: `emp-${String(i+1).padStart(3,'0')}`,
  name: `${f} ${pick(LAST)}`,
  team: ["platform","product","data","mobile","infra"][i%5],
  archetype: ARCH_KEYS[i%ARCH_KEYS.length],
}));

// Peers = same team. Manager = team lead (fixed 5 managers = first of each team).
const managers = {};
for (const t of ["platform","product","data","mobile","infra"]){
  managers[t] = people.find(p=>p.team===t).id;
}

const quarters = [
  { q:"Q3-2026", start:"2026-07-01", end:"2026-09-30" },
  { q:"Q4-2026", start:"2026-10-01", end:"2026-12-31" },
];

function* evidence(){
  let n = 0;
  for (const qq of quarters){
    for (const p of people){
      // persona quarter flip for 'improving'
      let posP = PERSONAS[p.archetype].pos;
      if (p.archetype==='improving' && qq.q==='Q4-2026') posP = 0.75;
      if (p.archetype==='volatile') posP = qq.q==='Q3-2026' ? 0.75 : 0.35;
      const roles = [
        { rater: p.id, role:"self" },
        { rater: pick(people.filter(x=>x.team===p.team && x.id!==p.id)).id, role:"peer" },
        { rater: managers[p.team], role:"manager" },
      ];
      const perRole = { self: 3, peer: 5, manager: 4 }; // ~12 incidents/person/quarter
      for (const r of roles){
        for (let i=0;i<perRole[r.role];i++){
          const sentiment = rnd()<posP ? "pos" : "neg";
          const comp = pick(COMPETENCIES);
          const subject = pick(SUBJECTS);
          // event time: random day in quarter
          const d = new Date(qq.start); d.setDate(d.getDate()+Math.floor(rnd()*92));
          const eventTime = d.toISOString().slice(0,10);
          // ingestion time: 0-14 days after event
          const di = new Date(d); di.setDate(di.getDate()+Math.floor(rnd()*15));
          const ingTime = di.toISOString().slice(0,10);
          n++;
          yield {
            id: `ev-${String(n).padStart(5,'0')}`,
            person_id: p.id,
            person_name: p.name,
            team: p.team,
            rater_id: r.rater,
            rater_role: r.role,
            quarter: qq.q,
            competency: comp,
            sentiment,
            quote: makeQuote(p.archetype, sentiment, comp, subject),
            event_time: eventTime,
            ingestion_time: ingTime,
          };
        }
      }
    }
  }
}

const all = [...evidence()];
import { writeFileSync } from 'fs';
writeFileSync('evidence.json', JSON.stringify(all, null, 2));
console.log(`generated ${all.length} evidence records for ${people.length} people over 2 quarters`);
console.log(`roles: self=${all.filter(e=>e.rater_role==='self').length} peer=${all.filter(e=>e.rater_role==='peer').length} manager=${all.filter(e=>e.rater_role==='manager').length}`);
console.log(`sentiment: pos=${all.filter(e=>e.sentiment==='pos').length} neg=${all.filter(e=>e.sentiment==='neg').length}`);
console.log(`sample: ${JSON.stringify(all[0])}`);
console.log(`sample improving (emp-004): ${all.filter(e=>e.person_id==='emp-004').slice(0,2).map(e=>`${e.quarter}/${e.sentiment}`).join(', ')}`);
