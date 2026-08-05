import type {Review} from "./review.js";
export type Attempt={exerciseId:string;rule:string;correct:boolean;at:string};
export function streak(attempts:Attempt[]){let count=0;for(const item of [...attempts].sort((a,b)=>Date.parse(b.at)-Date.parse(a.at))){if(!item.correct)break;count++}return count}
export function reviewLoad(reviews:Review[],now=new Date()){const due=reviews.filter(x=>Date.parse(x.due)<=now.valueOf()).length;const leeches=reviews.filter(x=>x.attempts>=5&&x.ease<=1.5).map(x=>x.exerciseId);return{due,total:reviews.length,leeches}}
export function dailyAccuracy(attempts:Attempt[]){const grouped=new Map<string,boolean[]>();for(const x of attempts){const day=x.at.slice(0,10);grouped.set(day,[...(grouped.get(day)??[]),x.correct])}return[...grouped].sort().map(([date,v])=>({date,accuracy:v.filter(Boolean).length/v.length,attempts:v.length}))}
