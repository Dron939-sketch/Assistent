import { ADDONS } from "@/lib/pricing";

export function Addons() {
  return (
    <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {ADDONS.map((a) => (
        <li
          key={a.id}
          className="flex flex-col rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
        >
          <div className="flex items-baseline justify-between gap-2">
            <h3 className="text-sm font-semibold text-gray-900">{a.name}</h3>
            <span className="text-xs font-medium text-emerald-700">
              {a.price}
            </span>
          </div>
          <p className="mt-2 flex-1 text-sm text-gray-700">{a.description}</p>
        </li>
      ))}
    </ul>
  );
}
